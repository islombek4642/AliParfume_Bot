from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.localization import I18N
from data.constants import MenuKeys

def get_contact_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=I18N.get("share_contact", lang), request_contact=True)]
        ],
        resize_keyboard=True
    )

def get_main_menu_keyboard(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=I18N.get(MenuKeys.CATALOG, lang)), KeyboardButton(text=I18N.get(MenuKeys.CART, lang))],
        [KeyboardButton(text=I18N.get(MenuKeys.ORDERS, lang)), KeyboardButton(text=I18N.get("btn_about", lang))],
        [KeyboardButton(text=I18N.get(MenuKeys.SETTINGS, lang))]
    ]
    
    if is_admin:
        # Add admin buttons to the bottom
        keyboard.append([KeyboardButton(text=I18N.get("admin_btn_stats", lang)), KeyboardButton(text=I18N.get("admin_btn_broadcast", lang))])
        keyboard.append([KeyboardButton(text=I18N.get("admin_btn_add_product", lang))])
        
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def get_categories_keyboard(lang: str, categories: list) -> ReplyKeyboardMarkup:
    keyboard_buttons = []
    for cat in categories:
        name = cat.name_uz if lang == "uz" else cat.name_ru
        keyboard_buttons.append([KeyboardButton(text=name)])
    
    keyboard_buttons.append([KeyboardButton(text=I18N.get(MenuKeys.BACK, lang))])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )

def get_lang_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=I18N.get("lang_uz", "uz")), KeyboardButton(text=I18N.get("lang_ru", "ru"))]
        ],
        resize_keyboard=True
    )

def get_quantity_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
            [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")],
            [KeyboardButton(text="7"), KeyboardButton(text="8"), KeyboardButton(text="9")],
            [KeyboardButton(text=I18N.get(MenuKeys.BACK, lang))]
        ],
        resize_keyboard=True
    )

def get_cart_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=I18N.get("btn_order_confirm", lang))],
            [KeyboardButton(text=I18N.get("btn_cart_delete", lang))],
            [KeyboardButton(text=I18N.get("btn_cart_clear", lang))],
            [KeyboardButton(text=I18N.get(MenuKeys.BACK, lang))]
        ],
        resize_keyboard=True
    )

def get_products_keyboard(lang: str, products: list) -> ReplyKeyboardMarkup:
    keyboard_buttons = []
    for prod in products:
        name = prod.name_uz if lang == "uz" else prod.name_ru
        keyboard_buttons.append([KeyboardButton(text=f"🛒 {name}")])
    
    keyboard_buttons.append([KeyboardButton(text=I18N.get(MenuKeys.BACK, lang))])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )

def get_cart_delete_keyboard(lang: str, cart_items: list) -> ReplyKeyboardMarkup:
    keyboard_buttons = []
    for name, prod_id in cart_items:
        keyboard_buttons.append([KeyboardButton(text=f"❌ {name}")])
    
    keyboard_buttons.append([KeyboardButton(text=I18N.get(MenuKeys.BACK, lang))])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )

def get_admin_cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=I18N.get("admin_btn_cancel", lang))]
        ],
        resize_keyboard=True
    )

def get_confirmation_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=I18N.get("admin_btn_yes", lang)), KeyboardButton(text=I18N.get("admin_btn_no", lang))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


