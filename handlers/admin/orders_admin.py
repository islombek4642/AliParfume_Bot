from aiogram import Router, F, Bot, types
from sqlalchemy.ext.asyncio import AsyncSession
from services.order_service import OrderService
from services.product_service import ProductService
from keyboards.inline import get_order_admin_keyboard
from data.constants import OrderKeys
from utils.localization import I18N

router = Router()

# Status → popup label (bilingual, from JSON)
STATUS_LABEL_KEY = {
    "processing": OrderKeys.STATUS_PROCESSING,
    "shipped":    OrderKeys.STATUS_SHIPPED,
    "completed":  OrderKeys.STATUS_COMPLETED,
    "cancelled":  OrderKeys.STATUS_CANCELLED,
}

# Status → DM message key per language
STATUS_DM_KEY = {
    "processing": OrderKeys.DM_PROCESSING,
    "shipped":    OrderKeys.DM_SHIPPED,
    "completed":  OrderKeys.DM_COMPLETED,
    "cancelled":  OrderKeys.DM_CANCELLED,
}


@router.callback_query(F.data.startswith("order_status:"))
async def handle_order_status(callback: types.CallbackQuery, session: AsyncSession, bot: Bot):
    parts = callback.data.split(":")
    order_id = int(parts[1])
    new_status = parts[2]

    order_service = OrderService(session)
    product_service = ProductService(session)

    order = await order_service.update_status(order_id, new_status)
    if not order:
        await callback.answer("Buyurtma topilmadi! / Заказ не найден!", show_alert=True)
        return

    # Restore stock if cancelled
    if new_status == "cancelled" and order.items:
        for product_id_str, quantity in order.items.items():
            await product_service.update_stock(int(product_id_str), quantity)

    # ✅ Only edit the KEYBOARD — never touch the channel message text
    new_keyboard = get_order_admin_keyboard(order_id, new_status)
    try:
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    except Exception as edit_err:
        import logging
        logging.warning(f"Could not edit keyboard for order {order_id}: {edit_err}")

    # DM the customer in their language
    try:
        from sqlalchemy import select
        from database.models import User
        result = await session.execute(select(User).where(User.id == order.user_id))
        customer = result.scalar_one_or_none()

        if customer:
            lang = getattr(customer, "language", "uz") or "uz"
            dm_key = STATUS_DM_KEY.get(new_status)
            if dm_key:
                dm_text = I18N.get(dm_key, lang).format(id=order_id)
                await bot.send_message(customer.telegram_id, dm_text)
    except Exception as dm_err:
        import logging
        logging.warning(f"Could not DM customer for order {order_id}: {dm_err}")

    # Bilingual popup (same text in both languages)
    label_key = STATUS_LABEL_KEY.get(new_status, "")
    label = I18N.get(label_key, "uz") if label_key else new_status
    await callback.answer(f"✅ {label}", show_alert=False)
