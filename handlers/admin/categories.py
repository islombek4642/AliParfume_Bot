from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.category_service import CategoryService
from keyboards.reply import get_main_menu_keyboard, get_admin_cancel_keyboard, get_categories_keyboard
from data.config import CONFIG
from data.constants import AdminKeys, AdminStates
from utils.localization import I18N

router = Router()

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all(AdminKeys.CATEGORIES)))
async def admin_categories_menu(message: Message, session: AsyncSession, _, lang):
    cat_service = CategoryService(session)
    cats = await cat_service.get_all()
    lines = "\n".join(f"  • {c.name_uz} / {c.name_ru}  [{c.slug}]" for c in cats) or "  —"
    await message.answer(
        _("admin_cat_list_header").format(count=len(cats), lines=lines),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, True) # Show main with admin buttons
    )

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all(AdminKeys.CAT_ADD)))
async def cat_add_start(message: Message, state: FSMContext, _, lang):
    await state.set_state(AdminStates.ADD_PRODUCT_CAT) # Reuse or use specific
    await message.answer(_("admin_cat_add_name_uz"), reply_markup=get_admin_cancel_keyboard(lang))

@router.message(AdminStates.ADD_PRODUCT_CAT) # Simplified for example
async def cat_add_process(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all(AdminKeys.CANCELLED):
        await state.clear()
        await message.answer(_("admin_broadcast_cancelled"), reply_markup=get_main_menu_keyboard(lang, True))
        return
    
    # Logic for adding category (simplified for demonstration)
    # In real app, this would be a multi-step FSM
    await message.answer("Tez orada qo'shiladi (FSM refaktoring davom etmoqda)...")
    await state.clear()
