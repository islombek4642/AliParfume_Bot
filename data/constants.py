from enum import Enum

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

class AdminKeys(str, Enum):
    STATS = "admin_stats"
    ADD_PRODUCT = "admin_add_product"
    EDIT_PRODUCT = "admin_edit_product"
    DELETE_PRODUCT = "admin_delete_product"
    MAILING = "admin_mailing"

class UserStates(str, Enum):
    # FSM States as strings for easy identification
    SELECT_CATEGORY = "SELECT_CATEGORY"
    SELECT_PRODUCT = "SELECT_PRODUCT"
    ENTER_QUANTITY = "ENTER_QUANTITY"
    ENTER_ADDRESS = "ENTER_ADDRESS"
    CONFIRM_ORDER = "CONFIRM_ORDER"

class AdminStates(str, Enum):
    # Admin FSM States
    SELECT_ACTION = "SELECT_ACTION"
    ADD_PRODUCT_PHOTO = "ADD_PRODUCT_PHOTO"
    ADD_PRODUCT_NAME_UZ = "ADD_PRODUCT_NAME_UZ"
    ADD_PRODUCT_NAME_RU = "ADD_PRODUCT_NAME_RU"
    ADD_PRODUCT_DESC_UZ = "ADD_PRODUCT_DESC_UZ"
    ADD_PRODUCT_DESC_RU = "ADD_PRODUCT_DESC_RU"
    ADD_PRODUCT_PRICE = "ADD_PRODUCT_PRICE"
    ADD_PRODUCT_CAT = "ADD_PRODUCT_CAT"
    MAILING_TEXT = "MAILING_TEXT"
