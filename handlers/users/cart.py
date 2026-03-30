from aiogram import Router, F, Bot, types
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService
from services.cart_service import CartService
from keyboards.reply import (
    get_quantity_keyboard, get_main_menu_keyboard, 
    get_cart_keyboard, get_cart_delete_keyboard,
    get_location_keyboard, get_checkout_keyboard
)
from keyboards.inline import get_order_admin_keyboard, get_my_orders_keyboard
from utils.localization import I18N
from data.config import CONFIG
from data.constants import MenuKeys, UserStates, ProductCallback, OrderCallback
from sqlalchemy.ext.asyncio import AsyncSession
import logging

router = Router()

@router.message(F.text.in_(I18N.get_all(MenuKeys.CART)))
async def view_cart(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    product_service = ProductService(session)
    cart_service = CartService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    if not user:
        await message.answer(_("error_user_not_found"))
        return
        
    items = await cart_service.get_items(user.id)
    if not items:
        await message.answer(_("cart_empty"))
        return

    text = _("cart_header")
    total_price = 0
    
    for item in items:
        product = await product_service.get_by_id(item.product_id)
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            price = product.price * item.quantity
            total_price += price
            text += f"• {name} x {item.quantity} = {price:,.0f} so'm\n"

    text += f"\n{_('cart_total')}{total_price:,.0f} so'm"
    await message.answer(text, reply_markup=get_cart_keyboard(lang))

@router.message(F.text.in_(I18N.get_all(MenuKeys.CLEAR_CART)))
async def cmd_clear_cart(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    cart_service = CartService(session)
    user = await user_service.get_by_id(message.from_user.id)
    
    await cart_service.clear_cart(user.id)
    await message.answer(_("cart_empty"), reply_markup=get_main_menu_keyboard(lang, user.is_admin))

# Checkout Flow
@router.message(F.text.in_(I18N.get_all(MenuKeys.CHECKOUT)))
async def checkout_start(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    cart_service = CartService(session)
    user = await user_service.get_by_id(message.from_user.id)
    
    items = await cart_service.get_items(user.id)
    if not items:
        await message.answer(_("cart_empty"))
        return
    
    await state.set_state(UserStates.ENTER_ADDRESS)
    await message.answer(_("checkout_ask_address"), reply_markup=get_location_keyboard(lang))

@router.message(UserStates.ENTER_ADDRESS)
async def checkout_process_address(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all("btn_cancel_checkout"):
        await state.clear()
        user_service = UserService(session)
        user = await user_service.get_by_id(message.from_user.id)
        await message.answer(_("checkout_cancelled"), reply_markup=get_main_menu_keyboard(lang, user.is_admin))
        return

    address = ""
    if message.location:
        address = f'<a href="https://maps.google.com/?q={message.location.latitude},{message.location.longitude}">📍 Xaritada</a>'
    elif message.text:
        address = message.text
    else:
        await message.answer(_("checkout_ask_address"))
        return

    await state.update_data(address=address)
    
    # Calculate order summary
    user_service = UserService(session)
    cart_service = CartService(session)
    product_service = ProductService(session)
    user = await user_service.get_by_id(message.from_user.id)
    items = await cart_service.get_items(user.id)
    
    items_text = ""
    total_price = 0
    for item in items:
        product = await product_service.get_by_id(item.product_id)
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            price = product.price * item.quantity
            total_price += price
            items_text += f"- {name} (x{item.quantity}) = {price:,.0f} so'm\n"

    invoice = _("checkout_invoice").format(items=items_text, address=address, total=f"{total_price:,.0f}")
    await state.set_state(UserStates.CONFIRM_ORDER)
    await message.answer(invoice, parse_mode="HTML", reply_markup=get_checkout_keyboard(lang), link_preview_options=LinkPreviewOptions(is_disabled=True))

@router.message(UserStates.CONFIRM_ORDER, F.text.in_(I18N.get_all(MenuKeys.CHECKOUT)))
async def checkout_confirm_final(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, _, lang):
    user_service = UserService(session)
    cart_service = CartService(session)
    order_service = OrderService(session)
    product_service = ProductService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    items = await cart_service.get_items(user.id)
    data = await state.get_data()
    address = data.get("address")

    if not items:
        await state.clear()
        return

    # Calculate total price correctly using loaded product relations
    total_price = sum(item.product.price * item.quantity for item in items if item.product)
    
    # Create order with OrderItems (relational)
    order = await order_service.create(user.id, items, total_price, address=address)
    
    # Stock update and notify
    for item in items:
        if item.product:
            await product_service.update_stock(item.product_id, -item.quantity)
            # Notify admins if product out of stock
            if item.product.stock <= 0:
                for admin_id in CONFIG.admin_ids:
                    try:
                        await bot.send_message(admin_id, f"⚠️ Mahsulot tugadi: {item.product.name_uz}")
                    except: pass

    # Send order to channel
    if CONFIG.CHANNEL_ID:
        try:
            kb = get_order_admin_keyboard(order.id)
            await bot.send_message(CONFIG.CHANNEL_ID, f"📦 Buyurtma #{order.id}\n👤 {user.full_name}\n📍 {address}\n💰 {total_price:,.0f}", reply_markup=kb)
        except Exception as e:
            logging.error(f"Channel notify error: {e}")

    await cart_service.clear_cart(user.id)
    await state.clear()
    await message.answer(_("order_forwarded"), reply_markup=get_main_menu_keyboard(lang, user.is_admin))
