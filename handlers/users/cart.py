from aiogram import Router, F, Bot, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService
from keyboards.reply import get_quantity_keyboard, get_main_menu_keyboard, get_cart_keyboard, get_cart_delete_keyboard
from utils.localization import I18N
from data.config import CONFIG
from data.constants import MenuKeys
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

class CartState(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_delete = State()

class CheckoutState(StatesGroup):
    waiting_for_address = State()
    waiting_for_confirmation = State()


@router.message(F.text.startswith("🛒"), ~F.text.in_(I18N.get_all(MenuKeys.CART)))
async def start_add_to_cart(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    product_service = ProductService(session)
    product_name = message.text.replace("🛒 ", "")
    
    product = await product_service.search_by_name(product_name)
    
    if product:
        await state.update_data(product_id=product.id)
        await state.set_state(CartState.waiting_for_quantity)
        await message.answer(_("select_quantity"), reply_markup=get_quantity_keyboard(lang))
@router.callback_query(F.data.startswith("buy_inline:"))
async def start_add_to_cart_inline(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, _, lang):
    product_id = int(callback.data.split(":")[1])
    await state.update_data(product_id=product_id)
    await state.set_state(CartState.waiting_for_quantity)
    
    # We delete the original inline message to keep things clean or just answer
    await callback.message.answer(_("select_quantity"), reply_markup=get_quantity_keyboard(lang))
    await callback.answer()

@router.message(CartState.waiting_for_quantity, F.text.regexp(r"^\d+$"))
async def set_quantity(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    quantity = int(message.text)
    data = await state.get_data()
    product_id = data.get("product_id")
    
    if product_id:
        await user_service.add_to_cart(message.from_user.id, product_id, quantity)
        is_admin = CONFIG.is_admin(message.from_user.id)
        await message.answer(_("cart_add_success"), reply_markup=get_main_menu_keyboard(lang, is_admin))
        await state.clear()

@router.message(F.text.in_(I18N.get_all(MenuKeys.CART)))
async def view_cart(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    product_service = ProductService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    if not user or not user.cart:
        await message.answer(_("cart_empty"))
        return

    text = _("cart_header")
    total_price = 0
    
    for product_id_str, quantity in user.cart.items():
        product = await product_service.get_by_id(int(product_id_str))
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            price = product.price * quantity
            total_price += price
            text += f"• {name} x {quantity} = {price:,} so'm\n"

    text += f"{_('cart_total')}{total_price:,} so'm"
    await message.answer(text, reply_markup=get_cart_keyboard(lang))

@router.message(F.text.in_(I18N.get_all("btn_cart_clear")))
async def cmd_clear_cart(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    await user_service.clear_cart(message.from_user.id)
    is_admin = CONFIG.is_admin(message.from_user.id)
    await message.answer(_("cart_empty"), reply_markup=get_main_menu_keyboard(lang, is_admin))

@router.message(F.text.in_(I18N.get_all("btn_order_confirm")))
async def checkout_start(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    user = await user_service.get_by_id(message.from_user.id)
    if not user or not user.cart:
        await message.answer(_("cart_empty"))
        return
    
    from keyboards.reply import get_location_keyboard
    await state.set_state(CheckoutState.waiting_for_address)
    await message.answer(_("checkout_ask_address"), reply_markup=get_location_keyboard(lang))

@router.message(CheckoutState.waiting_for_address)
async def checkout_process_address(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    from keyboards.reply import get_main_menu_keyboard, get_checkout_keyboard
    
    if message.text and message.text in I18N.get_all("btn_cancel_checkout"):
        await state.clear()
        is_admin = CONFIG.is_admin(message.from_user.id)
        await message.answer(_("checkout_cancelled"), reply_markup=get_main_menu_keyboard(lang, is_admin))
        return

    address = ""
    if message.location:
        address = f"<a href='https://maps.google.com/?q={message.location.latitude},{message.location.longitude}'>📍 Xaritada ko'rish</a>"
    elif message.text:
        address = message.text
    else:
        await message.answer(_("checkout_ask_address"))
        return

    await state.update_data(address=address)

    user_service = UserService(session)
    product_service = ProductService(session)
    user = await user_service.get_by_id(message.from_user.id)
    
    items_text = ""
    total_price = 0
    for product_id_str, quantity in user.cart.items():
        product = await product_service.get_by_id(int(product_id_str))
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            price = product.price * quantity
            total_price += price
            items_text += f"- {name} (x{quantity}) = {price:,.0f} so'm\n"

    invoice = _("checkout_invoice").format(
        items=items_text,
        address=address,
        total=f"{total_price:,.0f}" if total_price.is_integer() else f"{total_price:,}"
    )

    await state.set_state(CheckoutState.waiting_for_confirmation)
    await message.answer(invoice, parse_mode="HTML", reply_markup=get_checkout_keyboard(lang))

@router.message(CheckoutState.waiting_for_confirmation)
async def checkout_confirm_final(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, _, lang):
    from keyboards.reply import get_main_menu_keyboard
    
    if message.text in I18N.get_all("btn_cancel_checkout"):
        await state.clear()
        is_admin = CONFIG.is_admin(message.from_user.id)
        await message.answer(_("checkout_cancelled"), reply_markup=get_main_menu_keyboard(lang, is_admin))
        return

    if message.text not in I18N.get_all("btn_order_confirm"):
        await message.answer(_("checkout_confirm_prompt"))
        return

    user_service = UserService(session)
    product_service = ProductService(session)
    order_service = OrderService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    if not user or not user.cart:
        await state.clear()
        await message.answer(_("cart_empty"))
        return

    data = await state.get_data()
    address = data.get("address", "Belgilanmagan")

    items_text = ""
    total_price = 0
    for product_id_str, quantity in user.cart.items():
        product = await product_service.get_by_id(int(product_id_str))
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            price = product.price * quantity
            total_price += price
            items_text += f"- {name} (x{quantity})\n"

    # Create order in DB with address
    await order_service.create(user.id, user.cart, total_price, address=address)
    
    # Send to Channel
    try:
        channel_msg = I18N.get("order_success_channel", "uz").format(
            name=user.full_name,
            user_id=message.from_user.id,
            phone=user.phone,
            address=address,
            items=items_text,
            total=f"{total_price:,.0f}" if total_price.is_integer() else f"{total_price:,}"
        )
        if hasattr(CONFIG, 'CHANNEL_ID') and CONFIG.CHANNEL_ID:
            await bot.send_message(CONFIG.CHANNEL_ID, channel_msg, parse_mode="HTML")
    except Exception as e:
        import logging
        logging.error(f"⚠️ Buyurtmani kanalga yuborishda xatolik: {e}")

    # Clear Cart
    await user_service.clear_cart(message.from_user.id)
    await state.clear()
    
    is_admin = CONFIG.is_admin(message.from_user.id)
    await message.answer(_("order_forwarded"), reply_markup=get_main_menu_keyboard(lang, is_admin))

@router.message(F.text.in_(I18N.get_all(MenuKeys.ORDERS)))
async def cmd_my_orders(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    order_service = OrderService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    orders = await order_service.get_user_orders(user.id)
    
    if not orders:
        await message.answer(_("cart_empty"))
        return

    text = _("history_header")
    for order in orders[:10]: # Show last 10 orders
        date_str = order.created_at.strftime("%Y-%m-%d %H:%M")
        text += _("order_item").format(
            id=order.id,
            date=date_str,
            status=order.status,
            total=f"{order.total_price:,}"
        )
    
    await message.answer(text)

@router.message(F.text.in_(I18N.get_all("btn_cart_delete")))
async def cmd_cart_delete_start(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    product_service = ProductService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    if not user.cart:
        await message.answer(_("cart_empty"))
        return
    
    cart_items = []
    for prod_id_str, qty in user.cart.items():
        product = await product_service.get_by_id(int(prod_id_str))
        if product:
            name = product.name_uz if lang == "uz" else product.name_ru
            cart_items.append((name, product.id))
            
    await state.set_state(CartState.waiting_for_delete)
    await message.answer(_("delete_select"), reply_markup=get_cart_delete_keyboard(lang, cart_items))

@router.message(CartState.waiting_for_delete, F.text.startswith("❌"))
async def cmd_cart_delete_product(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    product_service = ProductService(session)
    
    product_name = message.text.replace("❌ ", "")
    product = await product_service.search_by_name(product_name)
    
    if product:
        await user_service.delete_from_cart(message.from_user.id, product.id)
        is_admin = CONFIG.is_admin(message.from_user.id)
        await message.answer(_("cart_delete_success"), reply_markup=get_main_menu_keyboard(lang, is_admin))
        await state.clear()
