from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from services.product_service import ProductService
from services.category_service import CategoryService
from keyboards.reply import get_categories_keyboard, get_main_menu_keyboard, get_admin_cancel_keyboard, get_confirmation_keyboard
from data.config import CONFIG
from data.constants import AdminStates, AdminKeys, ProductCallback
from sqlalchemy.ext.asyncio import AsyncSession
from utils.localization import I18N

router = Router()

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all(AdminKeys.ADD_PRODUCT)))
async def start_add_product(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await state.set_state(AdminStates.ADD_PRODUCT_CAT)
    await message.answer(_("admin_prompt_cat"), reply_markup=get_categories_keyboard(lang, categories))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_CAT))
async def process_category(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all(AdminKeys.CANCELLED):
        await state.clear()
        await message.answer(_("admin_broadcast_cancelled"), reply_markup=get_main_menu_keyboard(lang, True))
        return

    category_service = CategoryService(session)
    categories = await category_service.get_all()
    selected = next((c for c in categories if c.name_uz == message.text or c.name_ru == message.text), None)
    
    if not selected:
        await message.answer(_("admin_prompt_cat"))
        return
        
    await state.update_data(category_id=selected.id)
    await state.set_state(AdminStates.ADD_PRODUCT_NAME_UZ)
    await message.answer(_("admin_prompt_name_uz"), reply_markup=get_admin_cancel_keyboard(lang))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_NAME_UZ))
async def process_name_uz(message: Message, state: FSMContext, _, lang):
    await state.update_data(name_uz=message.text)
    await state.set_state(AdminStates.ADD_PRODUCT_NAME_RU)
    await message.answer(_("admin_prompt_name_ru"))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_NAME_RU))
async def process_name_ru(message: Message, state: FSMContext, _, lang):
    await state.update_data(name_ru=message.text)
    await state.set_state(AdminStates.ADD_PRODUCT_DESC_UZ)
    await message.answer(_("admin_prompt_desc_uz"))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_DESC_UZ))
async def process_desc_uz(message: Message, state: FSMContext, _, lang):
    await state.update_data(desc_uz=message.text)
    await state.set_state(AdminStates.ADD_PRODUCT_DESC_RU)
    await message.answer(_("admin_prompt_desc_ru"))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_DESC_RU))
async def process_desc_ru(message: Message, state: FSMContext, _, lang):
    await state.update_data(desc_ru=message.text)
    await state.set_state(AdminStates.ADD_PRODUCT_PRICE)
    await message.answer(_("admin_prompt_price"))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_PRICE))
async def process_price(message: Message, state: FSMContext, _, lang):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AdminStates.ADD_PRODUCT_PHOTO)
        await message.answer(_("admin_prompt_photo"))
    except ValueError:
        await message.answer(_("admin_prompt_price"))

@router.message(StateFilter(AdminStates.ADD_PRODUCT_PHOTO), F.photo)
async def process_photo(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    product_service = ProductService(session)
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    await product_service.create(
        data['category_id'],
        data['name_uz'],
        data['name_ru'],
        data['price'],
        data['desc_uz'],
        data['desc_ru'],
        photo_id,
        stock=100 # Default stock
    )
    
    await message.answer(_("admin_add_success"), reply_markup=get_main_menu_keyboard(lang, True))
    await state.clear()

# --- Edit & Delete Products ---

@router.callback_query(ProductCallback.filter(F.action == "delete"))
async def admin_delete_product(callback: CallbackQuery, callback_data: ProductCallback, session: AsyncSession, _):
    product_service = ProductService(session)
    await product_service.delete(callback_data.product_id)
    await callback.answer(_("cart_delete_success"))
    await callback.message.delete()

@router.callback_query(ProductCallback.filter(F.action == "edit_price"))
async def admin_edit_price_start(callback: CallbackQuery, callback_data: ProductCallback, state: FSMContext, _, lang):
    await state.set_state(AdminStates.EDIT_PRODUCT_VALUE)
    await state.update_data(product_id=callback_data.product_id, field="price")
    await callback.message.answer(_("admin_prompt_price"), reply_markup=get_admin_cancel_keyboard(lang))
    await callback.answer()

@router.callback_query(ProductCallback.filter(F.action == "edit_stock"))
async def admin_edit_stock_start(callback: CallbackQuery, callback_data: ProductCallback, state: FSMContext, _, lang):
    await state.set_state(AdminStates.EDIT_PRODUCT_VALUE)
    await state.update_data(product_id=callback_data.product_id, field="stock")
    await callback.message.answer(_("admin_prompt_stock"), reply_markup=get_admin_cancel_keyboard(lang))
    await callback.answer()

@router.message(StateFilter(AdminStates.EDIT_PRODUCT_VALUE))
async def admin_process_edit_value(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all(AdminKeys.CANCELLED):
        await state.clear()
        await message.answer(_("admin_broadcast_cancelled"), reply_markup=get_main_menu_keyboard(lang, True))
        return

    data = await state.get_data()
    product_id = data.get("product_id")
    field = data.get("field")
    
    try:
        val = float(message.text) if field == "price" else int(message.text)
        product_service = ProductService(session)
        await product_service.update_product(product_id, **{field: val})
        await message.answer(_("auth_success"), reply_markup=get_main_menu_keyboard(lang, True)) # Reusing success msg or adding new
        await state.clear()
    except ValueError:
        await message.answer(_("admin_prompt_price") if field == "price" else _("admin_prompt_stock"))
