from aiogram import Router, F, Bot, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from services.order_service import OrderService
from services.product_service import ProductService
from services.user_service import UserService
from keyboards.inline import get_order_admin_keyboard
from data.constants import OrderCallback, OrderKeys
from utils.localization import I18N
import logging

_ = I18N.get

router = Router()

@router.callback_query(OrderCallback.filter())
async def handle_order_status_admin(callback: CallbackQuery, callback_data: OrderCallback, session: AsyncSession, bot: Bot, _, lang):
    order_service = OrderService(session)
    product_service = ProductService(session)
    user_service = UserService(session)
    
    order = await order_service.get_by_id(callback_data.order_id)
    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    # Update status in DB
    await order_service.update_status(order.id, callback_data.status)
    
    # Restore stock if cancelled
    if callback_data.status == OrderKeys.STATUS_CANCELLED:
        for item in order.items:
            if item.product_id:
                await product_service.update_stock(item.product_id, item.quantity)

    # Notify customer
    customer = await user_service.get_by_id(order.user_id)
    
    if customer:
        try:
            status_msg = I18N.get(f"order_status_{callback_data.status}_user", customer.language)
            await bot.send_message(customer.telegram_id, _("order_dm_" + callback_data.status).format(id=order.id))
        except Exception as e:
            logging.warning(f"Failed to notify user {customer.telegram_id}: {e}")

    # Update inline keyboard in channel/chat
    new_kb = get_order_admin_keyboard(order.id, callback_data.status)
    await callback.message.edit_reply_markup(reply_markup=new_kb)
    await callback.answer(f"Status: {callback_data.status}")
