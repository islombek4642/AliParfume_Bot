from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from services.user_service import UserService
from keyboards.reply import get_contact_keyboard, get_main_menu_keyboard, get_lang_keyboard
from utils.localization import I18N
from data.constants import MenuKeys
from data.config import CONFIG
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    user = await user_service.get_by_id(message.from_user.id)
    
    if not user:
        # Default language for first-time users: uz
        await user_service.create(message.from_user.id, message.from_user.full_name, "uz")
        await message.answer(_("welcome"), reply_markup=get_contact_keyboard("uz"))
    elif not user.phone:
        await message.answer(_("welcome"), reply_markup=get_contact_keyboard(lang))
    else:
        is_admin = user.is_admin
        await message.answer(_("main_menu"), reply_markup=get_main_menu_keyboard(lang, is_admin))

@router.message(F.contact)
async def get_contact(message: Message, session: AsyncSession, _, lang):
    user_service = UserService(session)
    user = await user_service.get_by_id(message.from_user.id)
    
    if not user:
        user = await user_service.create(message.from_user.id, message.from_user.full_name, "uz")
    
    await user_service.update_phone(message.from_user.id, message.contact.phone_number)
    
    # Reload user to get updated data including is_admin
    user = await user_service.get_by_id(message.from_user.id)
    is_admin = user.is_admin
    
    await message.answer(_("auth_success"), reply_markup=get_main_menu_keyboard(lang, is_admin))

@router.message(Command("settings"))
@router.message(F.text.in_(I18N.get_all(MenuKeys.SETTINGS)))
async def cmd_settings(message: Message, _, lang):
    await message.answer(_("settings_lang"), reply_markup=get_lang_keyboard())

@router.message(Command("about"))
@router.message(F.text.in_(I18N.get_all("btn_about")))
async def cmd_about(message: Message, _):
    await message.answer(_("about_text"))

@router.message(F.text.in_(I18N.get_all("lang_uz")))
@router.message(F.text.in_(I18N.get_all("lang_ru")))
async def set_lang(message: Message, session: AsyncSession, _):
    user_service = UserService(session)
    new_lang = "uz" if message.text in I18N.get_all("lang_uz") else "ru"
    
    await user_service.update_language(message.from_user.id, new_lang)
    user = await user_service.get_by_id(message.from_user.id)
    is_admin = user.is_admin if user else False
    
    await message.answer(
        I18N.get("lang_changed", new_lang), 
        reply_markup=get_main_menu_keyboard(new_lang, is_admin)
    )
