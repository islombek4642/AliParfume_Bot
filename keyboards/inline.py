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


def get_order_admin_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for admin channel order tickets — status management."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Qabul qilish", callback_data=f"order_status:{order_id}:processing"),
            InlineKeyboardButton(text="🚚 Yo'lda", callback_data=f"order_status:{order_id}:shipped"),
        ],
        [
            InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"order_status:{order_id}:completed"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"order_status:{order_id}:cancelled"),
        ]
    ])


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
