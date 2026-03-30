from enum import Enum
from aiogram.filters.callback_data import CallbackData

class MenuKeys(str, Enum):
    CATALOG = "btn_catalog"
    CART = "btn_cart"
    ORDERS = "btn_orders"
    SETTINGS = "btn_settings"
    CONTACT = "btn_contact"
    BACK = "btn_back"
    MAIN = "btn_main"
    ADD_TO_CART = "btn_add_to_cart"
    CLEAR_CART = "btn_clear_cart"
    CHECKOUT = "btn_checkout"
    SEARCH = "btn_search"

class AdminKeys(str, Enum):
    STATS = "admin_stats"
    ADD_PRODUCT = "admin_add_product"
    EDIT_PRODUCT = "admin_edit_product"
    DELETE_PRODUCT = "admin_delete_product"
    MAILING = "admin_mailing"
    CATEGORIES = "admin_btn_categories"
    CAT_ADD = "admin_btn_cat_add"
    CAT_DELETE = "admin_btn_cat_delete"
    CANCELLED = "admin_cancelled"
    EXPORT_USERS = "admin_btn_export_users"
    EXPORT_ORDERS = "admin_btn_export_orders"

class OrderKeys(str, Enum):
    BTN_ACCEPT       = "order_btn_accept"
    BTN_CANCEL_ORDER = "order_btn_cancel_order"
    BTN_SHIPPING     = "order_btn_shipping"
    BTN_DELIVERED    = "order_btn_delivered"
    STATUS_PENDING    = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED    = "shipped"
    STATUS_COMPLETED  = "completed"
    STATUS_CANCELLED  = "cancelled"

# Callback Data Classes
class ProductCallback(CallbackData, prefix="prod"):
    category_id: int
    index: int
    product_id: int
    action: str = "view" # view, buy, edit, delete, stock

class CategoryCallback(CallbackData, prefix="cat"):
    category_id: int

class OrderCallback(CallbackData, prefix="order"):
    order_id: int
    status: str

class PaginationCallback(CallbackData, prefix="pag"):
    page: int
    action: str

class SearchCallback(CallbackData, prefix="src"):
    query: str

# FSM States
class UserStates(str, Enum):
    SELECT_CATEGORY = "SELECT_CATEGORY"
    SELECT_PRODUCT = "SELECT_PRODUCT"
    ENTER_QUANTITY = "ENTER_QUANTITY"
    ENTER_ADDRESS = "ENTER_ADDRESS"
    CONFIRM_ORDER = "CONFIRM_ORDER"
    SEARCH_PRODUCT = "SEARCH_PRODUCT"

class AdminStates(str, Enum):
    SELECT_ACTION = "SELECT_ACTION"
    ADD_PRODUCT_PHOTO = "ADD_PRODUCT_PHOTO"
    ADD_PRODUCT_NAME_UZ = "ADD_PRODUCT_NAME_UZ"
    ADD_PRODUCT_NAME_RU = "ADD_PRODUCT_NAME_RU"
    ADD_PRODUCT_DESC_UZ = "ADD_PRODUCT_DESC_UZ"
    ADD_PRODUCT_DESC_RU = "ADD_PRODUCT_DESC_RU"
    ADD_PRODUCT_PRICE = "ADD_PRODUCT_PRICE"
    ADD_PRODUCT_CAT = "ADD_PRODUCT_CAT"
    MAILING_TEXT = "MAILING_TEXT"
    MAILING_MEDIA = "MAILING_MEDIA"
    MAILING_BUTTON = "MAILING_BUTTON"
    EDIT_PRODUCT_SELECT = "EDIT_PRODUCT_SELECT"
    EDIT_PRODUCT_FIELD = "EDIT_PRODUCT_FIELD"
    EDIT_PRODUCT_VALUE = "EDIT_PRODUCT_VALUE"
