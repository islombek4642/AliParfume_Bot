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
