from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.localization import I18N

def get_product_inline_keyboard(lang: str, category_id: int, current_index: int, total_count: int, product_id: int) -> InlineKeyboardMarkup:
    # Navigation buttons
    nav_buttons = []
    
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(
            text=I18N.get("btn_prev", lang),
            callback_data=f"prod_page:{category_id}:{current_index - 1}"
        ))
    
    nav_buttons.append(InlineKeyboardButton(
        text=I18N.get("product_count", lang).format(current=current_index + 1, total=total_count),
        callback_data="noop"
    ))
    
    if current_index < total_count - 1:
        nav_buttons.append(InlineKeyboardButton(
            text=I18N.get("btn_next", lang),
            callback_data=f"prod_page:{category_id}:{current_index + 1}"
        ))
    
    # Assembly
    buttons = [
        nav_buttons,
        [InlineKeyboardButton(
            text=I18N.get("btn_buy_inline", lang),
            callback_data=f"buy_inline:{product_id}"
        )],
        [InlineKeyboardButton(
            text=I18N.get("btn_back", lang),
            callback_data=f"back_to_cats"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



# Sequential flow: each status → next possible actions
_ORDER_STATUS_FLOW = {
    "pending":    [("✅ Qabul qilish / Принять",    "processing"),
                   ("❌ Bekor qilish / Отменить",   "cancelled")],
    "processing": [("🚚 Yo'lda / В пути",           "shipped"),
                   ("❌ Bekor qilish / Отменить",   "cancelled")],
    "shipped":    [("✅ Yetkazildi / Доставлено",   "completed")],
    "completed":  [],
    "cancelled":  [],
}

def get_order_admin_keyboard(order_id: int, current_status: str = "pending") -> InlineKeyboardMarkup | None:
    """Sequential vertical keyboard for admin order management in the channel."""
    steps = _ORDER_STATUS_FLOW.get(current_status, [])
    if not steps:
        return None
    # Each button gets its own row — vertical layout
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"order_status:{order_id}:{next_s}")]
        for label, next_s in steps
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_my_orders_keyboard(orders: list, index: int) -> InlineKeyboardMarkup:
    """Paginated 'My Orders' keyboard for users."""
    total = len(orders)
    nav = []
    if index > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"my_orders:{index - 1}"))
    nav.append(InlineKeyboardButton(text=f"{index + 1} / {total}", callback_data="noop"))
    if index < total - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"my_orders:{index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[nav])
