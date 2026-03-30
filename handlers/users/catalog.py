from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.product_service import ProductService
from services.category_service import CategoryService
from services.cart_service import CartService
from services.user_service import UserService
from keyboards.reply import get_categories_keyboard, get_main_menu_keyboard, get_admin_cancel_keyboard
from keyboards.inline import get_product_inline, get_categories_inline
from utils.localization import I18N
from data.constants import MenuKeys, ProductCallback, CategoryCallback, UserStates, PaginationCallback
from data.config import CONFIG
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_PHOTO = "https://placehold.co/600x400/f5f5f5/999999.png?text=AliParfume\nRasm+Yo'q"

router = Router()

@router.message(F.text.in_(I18N.get_all(MenuKeys.CATALOG)))
async def show_categories(message: Message, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await message.answer(
        _("catalog_header"),
        reply_markup=get_categories_keyboard(lang, categories)
    )

# --- Search Functionality ---

@router.message(F.text.in_(I18N.get_all(MenuKeys.SEARCH)))
async def start_search(message: Message, state: FSMContext, _, lang):
    await state.set_state(UserStates.SEARCH_PRODUCT)
    await message.answer(_("search_prompt"), reply_markup=get_admin_cancel_keyboard(lang))

@router.message(UserStates.SEARCH_PRODUCT)
async def process_search(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all(MenuKeys.BACK):
        await state.clear()
        user_service = UserService(session)
        db_user = await user_service.get_by_id(message.from_user.id)
        await message.answer(_("main_menu"), reply_markup=get_main_menu_keyboard(lang, db_user.is_admin))
        return

    product_service = ProductService(session)
    products = await product_service.search_products(message.text)
    
    if not products:
        await message.answer(_("search_no_results"))
        return

    await state.clear()
    await state.update_data(search_query=message.text)
    # For search results, we reuse send_product_view but without category_id (set to 0)
    await send_product_view(message, products, 0, 0, lang, session, _)

# --- Catalog Navigation ---

@router.message(F.text.in_(I18N.get_all(MenuKeys.BACK)))
@router.message(F.text.in_(I18N.get_all(MenuKeys.MAIN)))
async def go_main(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    db_user = await user_service.get_by_id(message.from_user.id)
    is_admin = db_user.is_admin if db_user else False
    
    await message.answer(
        _("main_menu"),
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )

@router.message(F.text)
async def handle_category_selection(message: Message, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    product_service = ProductService(session)
    categories = await category_service.get_all()
    
    selected_category = next((c for c in categories if message.text in [c.name_uz, c.name_ru]), None)
    
    if selected_category:
        products = await product_service.get_all(selected_category.id)
        if not products:
            await message.answer(_("cart_empty"))
            return
        await send_product_view(message, products, 0, selected_category.id, lang, session, _)

async def send_product_view(message_obj, products, index, category_id, lang, session, _, edit=False):
    product = products[index]
    is_admin = False
    if hasattr(message_obj, "from_user"):
        user_service = UserService(session)
        user = await user_service.get_by_id(message_obj.from_user.id)
        is_admin = user.is_admin if user else False

    name = product.name_uz if lang == "uz" else product.name_ru
    desc = product.description_uz if lang == "uz" else product.description_ru
    caption = (
        f"<b>{name}</b>\n\n"
        f"<i>{_('product_desc')}{desc}</i>\n"
        f"<b>{_('product_price')}{product.price:,.0f} so'm</b>\n"
        + (_("stock_left").format(count=product.stock) if product.stock > 0 else _("out_of_stock"))
    )
    
    reply_markup = get_product_inline(category_id, index, len(products), product.id, lang, is_admin)
    photo = product.photo_id if product.photo_id and not product.photo_id.startswith("http") else DEFAULT_PHOTO
    
    if edit and isinstance(message_obj, CallbackQuery):
        await message_obj.message.edit_media(
            media=types.InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
            reply_markup=reply_markup
        )
    else:
        await message_obj.answer_photo(photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)

@router.callback_query(PaginationCallback.filter())
async def handle_pagination(callback: types.CallbackQuery, callback_data: PaginationCallback, session: AsyncSession, state: FSMContext, _, lang):
    # Retrieve current context (category or search)
    # For now, let's assume we need to know if it's search or category from callback_data or state
    # Simplification: we'll check state for search query
    data = await state.get_data()
    search_query = data.get("search_query")
    
    product_service = ProductService(session)
    if search_query:
        products = await product_service.search_products(search_query)
        cat_id = 0
    else:
        # We'd need category_id which is NOT in PaginationCallback anymore? 
        # Actually I should have kept it or used state. 
        # Let's fix PaginationCallback or just use state to store category_id.
        cat_id = data.get("current_category_id", 0)
        products = await product_service.get_all(cat_id)
    
    if not products:
        await callback.answer()
        return
        
    await send_product_view(callback, products, callback_data.page, cat_id, lang, session, _, edit=True)
    await callback.answer()

@router.callback_query(CategoryCallback.filter(F.category_id == 0))
async def handle_back_to_cats(callback: CallbackQuery, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await callback.message.delete()
    await callback.message.answer(_("catalog_header"), reply_markup=get_categories_keyboard(lang, categories))
    await callback.answer()
