from aiogram import Router, F, Bot, types
from sqlalchemy.ext.asyncio import AsyncSession
from services.order_service import OrderService
from services.product_service import ProductService
from keyboards.inline import get_order_admin_keyboard

router = Router()

# Bilingual status labels shown in the callback answer popup
STATUS_LABELS = {
    "processing": "📦 Qabul qilindi / Принят",
    "shipped":    "🚚 Yo'lda / В пути",
    "completed":  "✅ Yetkazildi / Доставлен",
    "cancelled":  "❌ Bekor qilindi / Отменён",
}

# DM templates per language per status
STATUS_DM = {
    "uz": {
        "processing": "📦 #{id}-raqamli buyurtmangiz qabul qilindi va tayyorlanmoqda!",
        "shipped":    "🚚 #{id}-raqamli buyurtmangiz yetkazib berishga chiqdi!",
        "completed":  "✅ #{id}-raqamli buyurtmangiz muvaffaqiyatli yetkazildi! Rahmat 🙏",
        "cancelled":  "❌ #{id}-raqamli buyurtmangiz bekor qilindi. Savollaringiz bo'lsa murojaat qiling.",
    },
    "ru": {
        "processing": "📦 Ваш заказ №{id} принят и готовится!",
        "shipped":    "🚚 Ваш заказ №{id} отправлен в доставку!",
        "completed":  "✅ Ваш заказ №{id} успешно доставлен! Спасибо за покупку 🙏",
        "cancelled":  "❌ Ваш заказ №{id} был отменён. Свяжитесь с нами при необходимости.",
    }
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
    # This prevents duplicate messages and preserves the original order info
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
            dm_template = STATUS_DM.get(lang, STATUS_DM["uz"]).get(new_status)
            if dm_template:
                dm_text = dm_template.format(id=order_id)
                await bot.send_message(customer.telegram_id, dm_text)
    except Exception as dm_err:
        import logging
        logging.warning(f"Could not DM customer for order {order_id}: {dm_err}")

    label = STATUS_LABELS.get(new_status, new_status)
    await callback.answer(f"✅ {label}", show_alert=False)
