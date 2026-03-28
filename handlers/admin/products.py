from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.product_service import ProductService
from services.category_service import CategoryService
from keyboards.reply import get_categories_keyboard, get_main_menu_keyboard
from data.config import CONFIG
from data.constants import AdminStates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.localization import I18N

router = Router()

class AddProductState(StatesGroup):
    waiting_for_category = State()
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_desc_uz = State()
    waiting_for_desc_ru = State()
    waiting_for_price = State()
    waiting_for_photo = State()

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all("admin_btn_add_product")))
async def start_add_product(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await state.set_state(AddProductState.waiting_for_category)
    await message.answer(_("admin_prompt_cat"), reply_markup=get_categories_keyboard(lang, categories))

@router.message(AddProductState.waiting_for_category)
async def process_category(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    selected_category = next((c for c in categories if c.name_uz == message.text or c.name_ru == message.text), None)
    
    if not selected_category:
        await message.answer(_("admin_prompt_cat")) # Retry
        return
        
    await state.update_data(category_id=selected_category.id)
    await state.set_state(AddProductState.waiting_for_name_uz)
    await message.answer(_("admin_prompt_name_uz"))

@router.message(AddProductState.waiting_for_name_uz)
async def process_name_uz(message: Message, state: FSMContext, _):
    await state.update_data(name_uz=message.text)
    await state.set_state(AddProductState.waiting_for_name_ru)
    await message.answer(_("admin_prompt_name_ru"))

@router.message(AddProductState.waiting_for_name_ru)
async def process_name_ru(message: Message, state: FSMContext, _):
    await state.update_data(name_ru=message.text)
    await state.set_state(AddProductState.waiting_for_desc_uz)
    await message.answer(_("admin_prompt_desc_uz"))

@router.message(AddProductState.waiting_for_desc_uz)
async def process_desc_uz(message: Message, state: FSMContext, _):
    await state.update_data(desc_uz=message.text)
    await state.set_state(AddProductState.waiting_for_desc_ru)
    await message.answer(_("admin_prompt_desc_ru"))

@router.message(AddProductState.waiting_for_desc_ru)
async def process_desc_ru(message: Message, state: FSMContext, _):
    await state.update_data(desc_ru=message.text)
    await state.set_state(AddProductState.waiting_for_price)
    await message.answer(_("admin_prompt_price"))

@router.message(AddProductState.waiting_for_price)
async def process_price(message: Message, state: FSMContext, _):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AddProductState.waiting_for_photo)
        await message.answer(_("admin_prompt_photo"))
    except ValueError:
        await message.answer(_("admin_prompt_price")) # Retry

@router.message(AddProductState.waiting_for_photo, F.photo)
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
        photo_id
    )
    
    await message.answer(_("admin_add_success"), reply_markup=get_main_menu_keyboard(lang, is_admin=True))
    await state.clear()
