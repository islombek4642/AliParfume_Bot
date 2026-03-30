from aiogram import Router, F
from aiogram.types import Message
from services.order_service import OrderService
from services.user_service import UserService
from utils.localization import I18N
from data.constants import MenuKeys
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.message(F.text.in_(I18N.get_all(MenuKeys.ORDERS)))
async def show_history(message: Message, session: AsyncSession, _, lang):
    order_service = OrderService(session)
    user_service = UserService(session)
    
    user = await user_service.get_by_id(message.from_user.id)
    if not user:
        await message.answer(_("cart_empty"))
        return
        
    orders = await order_service.get_user_orders(user.id)
    
    if not orders:
        await message.answer(_("history_header") + "\n" + _("cart_empty"))
        return
        
    text = _("history_header") + "\n"
    for order in orders:
        status_key = f"order_status_{order.status}_user"
        status_text = _(status_key)
        
        # Details about items in order
        items_text = ""
        for item in order.items:
            # We use item.name and item.price which are history snapshots
            name = item.name # This is stored name at time of order
            items_text += f"  - {name} ({item.quantity} шт.) — {item.price * item.quantity:,.0f}\n"
            
        text += _("order_item").format(
            id=order.id,
            date=order.created_at.strftime("%Y-%m-%d %H:%M"),
            status=status_text,
            total=f"{order.total_price:,.0f}"
        )
        text += items_text + "------------------\n"

    await message.answer(text)
