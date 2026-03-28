from aiogram import Router, F, Bot, types
from sqlalchemy.ext.asyncio import AsyncSession
from services.order_service import OrderService
from services.user_service import UserService
from services.product_service import ProductService
from keyboards.inline import get_order_admin_keyboard
from utils.localization import I18N
from utils.timezone import get_now

router = Router()

# Localized status labels
STATUS_LABELS = {
    "processing": "📦 Qabul qilindi",
    "shipped":    "🚚 Yetkazib berishga chiqdi",
    "completed":  "✅ Yetkazildi",
    "cancelled":  "❌ Bekor qilindi",
}

# Localized DM messages for each status (uz / ru)
STATUS_DM = {
    "uz": {
        "processing": "📦 #{id}-raqamli buyurtmangiz qabul qilindi va tayyorlanmoqda!",
        "shipped":    "🚚 #{id}-raqamli buyurtmangiz yetkazib berishga chiqdi!",
        "completed":  "✅ #{id}-raqamli buyurtmangiz muvaffaqiyatli yetkazildi! Xaridingiz uchun rahmat 🙏",
        "cancelled":  "❌ #{id}-raqamli buyurtmangiz bekor qilindi. Savollaringiz bo'lsa murojaat qiling.",
    },
    "ru": {
        "processing": "📦 Ваш заказ №{id} принят и готовится!",
        "shipped":    "🚚 Ваш заказ №{id} отправлен на доставку!",
        "completed":  "✅ Ваш заказ №{id} успешно доставлен! Спасибо за покупку 🙏",
        "cancelled":  "❌ Ваш заказ №{id} был отменён. Свяжитесь с нами, если есть вопросы.",
    }
}


@router.callback_query(F.data.startswith("order_status:"))
async def handle_order_status(callback: types.CallbackQuery, session: AsyncSession, bot: Bot):
    _, order_id_str, new_status = callback.data.split(":")
    order_id = int(order_id_str)

    order_service = OrderService(session)
    user_service = UserService(session)
    product_service = ProductService(session)

    order = await order_service.update_status(order_id, new_status)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    # If cancelled — restore stock
    if new_status == "cancelled" and order.items:
        for product_id_str, quantity in order.items.items():
            await product_service.update_stock(int(product_id_str), quantity)

    # Edit the channel message to show updated status
    status_label = STATUS_LABELS.get(new_status, new_status)
    current_text = callback.message.text or callback.message.caption or ""
    # Remove any existing status line, then append new one
    lines = [l for l in current_text.splitlines() if not l.startswith("📌 Status:")]
    lines.append(f"📌 Status: {status_label}")
    new_text = "\n".join(lines)

    try:
        await callback.message.edit_text(
            new_text,
            parse_mode="HTML",
            reply_markup=get_order_admin_keyboard(order_id)
        )
    except Exception:
        pass  # message unchanged, ignore

    # DM the customer
    try:
        # Get the user who placed this order
        from sqlalchemy import select
        from database.models import User
        result = await session.execute(select(User).where(User.id == order.user_id))
        customer = result.scalar_one_or_none()

        if customer:
            lang = customer.language or "uz"
            dm_template = STATUS_DM.get(lang, STATUS_DM["uz"]).get(new_status)
            if dm_template:
                dm_text = dm_template.format(id=order_id)
                await bot.send_message(customer.telegram_id, dm_text)
    except Exception as e:
        import logging
        logging.warning(f"Could not DM customer for order {order_id}: {e}")

    await callback.answer(f"✅ Status: {status_label}")
