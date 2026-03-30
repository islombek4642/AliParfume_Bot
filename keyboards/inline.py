from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.constants import ProductCallback, CategoryCallback, OrderCallback, PaginationCallback
from utils.localization import I18N

def get_categories_inline(categories: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        name = cat.name_uz if lang == "uz" else cat.name_ru
        builder.row(InlineKeyboardButton(text=name, callback_data=CategoryCallback(category_id=cat.id).pack()))
    return builder.as_markup()

def get_product_inline(category_id: int, index: int, total: int, product_id: int, lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Buy button
    builder.row(InlineKeyboardButton(text=I18N.get("btn_buy_inline", lang), callback_data=ProductCallback(category_id=category_id, index=index, product_id=product_id, action="buy").pack()))
    
    # Navigation buttons
    nav_btns = []
    if index > 0:
        nav_btns.append(InlineKeyboardButton(text=I18N.get("btn_prev", lang), callback_data=PaginationCallback(page=index - 1, action="prev").pack()))
    
    # Back to categories
    nav_btns.append(InlineKeyboardButton(text=I18N.get("btn_back", lang), callback_data=CategoryCallback(category_id=0).pack()))
    
    if index < total - 1:
        nav_btns.append(InlineKeyboardButton(text=I18N.get("btn_next", lang), callback_data=PaginationCallback(page=index + 1, action="next").pack()))
    
    builder.row(*nav_btns)
    
    # Admin Edit/Delete buttons
    if is_admin:
        builder.row(
            InlineKeyboardButton(text=I18N.get("admin_edit_price", lang), callback_data=ProductCallback(category_id=category_id, index=index, product_id=product_id, action="edit_price").pack()),
            InlineKeyboardButton(text=I18N.get("admin_edit_stock", lang), callback_data=ProductCallback(category_id=category_id, index=index, product_id=product_id, action="edit_stock").pack())
        )
        builder.row(
            InlineKeyboardButton(text="🗑 " + I18N.get("btn_cart_delete", lang), callback_data=ProductCallback(category_id=category_id, index=index, product_id=product_id, action="delete").pack())
        )
        
    return builder.as_markup()

def get_order_admin_keyboard(order_id: int, current_status: str = "pending") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if current_status == "pending":
        builder.row(InlineKeyboardButton(text=I18N.get("order_btn_accept", "uz"), callback_data=OrderCallback(order_id=order_id, status="processing").pack()))
    elif current_status == "processing":
        builder.row(InlineKeyboardButton(text=I18N.get("order_btn_shipping", "uz"), callback_data=OrderCallback(order_id=order_id, status="shipped").pack()))
    elif current_status == "shipped":
        builder.row(InlineKeyboardButton(text=I18N.get("order_btn_delivered", "uz"), callback_data=OrderCallback(order_id=order_id, status="completed").pack()))
        
    if current_status not in ["completed", "cancelled"]:
        builder.row(InlineKeyboardButton(text=I18N.get("order_btn_cancel_order", "uz"), callback_data=OrderCallback(order_id=order_id, status="cancelled").pack()))
        
    return builder.as_markup()

def get_my_orders_keyboard() -> InlineKeyboardMarkup:
    # Placeholder for pagination if needed
    return None
