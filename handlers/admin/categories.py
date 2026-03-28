from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from services.category_service import CategoryService
from keyboards.reply import get_main_menu_keyboard, get_admin_cancel_keyboard
from data.config import CONFIG
from data.constants import AdminKeys
from utils.localization import I18N

router = Router()

# ──────────────────────────── FSM ─────────────────────────────
class CategoryState(StatesGroup):
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_slug    = State()
    waiting_for_delete  = State()

# ──────────────────── Keyboard helpers ────────────────────────
def _admin_cat_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=I18N.get(AdminKeys.CAT_ADD, lang)),
         KeyboardButton(text=I18N.get(AdminKeys.CAT_DELETE, lang))],
        [KeyboardButton(text=I18N.get("admin_btn_cancel", lang))]
    ], resize_keyboard=True)

def _cat_list_keyboard(cats: list, lang: str) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=c.name_uz)] for c in cats]
    rows.append([KeyboardButton(text=I18N.get("admin_btn_cancel", lang))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

# ──────────────────── Entry point ─────────────────────────────
@router.message(F.from_user.id.in_(CONFIG.admin_ids),
                F.text.in_(I18N.get_all(AdminKeys.CATEGORIES)))
async def admin_categories_menu(message: Message, session: AsyncSession, _, lang):
    cat_service = CategoryService(session)
    cats = await cat_service.get_all()
    lines = "\n".join(f"  • {c.name_uz} / {c.name_ru}  [{c.slug}]" for c in cats) or "  —"
    await message.answer(
        I18N.get("admin_cat_list_header", lang).format(count=len(cats), lines=lines),
        parse_mode="HTML",
        reply_markup=_admin_cat_menu(lang)
    )

@router.message(StateFilter(None), F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all("admin_btn_cancel")))
async def admin_cat_cancel_main(message: Message, state: FSMContext, _, lang):
    """Handle 'Cancel' button from the category actions menu (State=None)"""
    await state.clear()
    await message.answer(
        I18N.get(AdminKeys.CANCELLED, lang),
        reply_markup=get_main_menu_keyboard(lang, True)
    )

# ──────────────────── ADD FLOW ────────────────────────────────
@router.message(F.from_user.id.in_(CONFIG.admin_ids),
                F.text.in_(I18N.get_all(AdminKeys.CAT_ADD)))
async def cat_add_start(message: Message, state: FSMContext, _, lang):
    await state.set_state(CategoryState.waiting_for_name_uz)
    await message.answer(I18N.get("admin_cat_add_name_uz", lang),
                         parse_mode="HTML",
                         reply_markup=get_admin_cancel_keyboard(lang))

@router.message(CategoryState.waiting_for_name_uz)
async def cat_add_name_uz(message: Message, state: FSMContext, _, lang):
    if message.text in I18N.get_all("admin_btn_cancel"):
        await state.clear()
        await message.answer(I18N.get(AdminKeys.CANCELLED, lang),
                             reply_markup=get_main_menu_keyboard(lang, True))
        return
    await state.update_data(name_uz=message.text.strip())
    await state.set_state(CategoryState.waiting_for_name_ru)
    await message.answer(I18N.get("admin_cat_add_name_ru", lang), parse_mode="HTML")

@router.message(CategoryState.waiting_for_name_ru)
async def cat_add_name_ru(message: Message, state: FSMContext, _, lang):
    if message.text in I18N.get_all("admin_btn_cancel"):
        await state.clear()
        await message.answer(I18N.get(AdminKeys.CANCELLED, lang),
                             reply_markup=get_main_menu_keyboard(lang, True))
        return
    await state.update_data(name_ru=message.text.strip())
    await state.set_state(CategoryState.waiting_for_slug)
    await message.answer(I18N.get("admin_cat_add_slug", lang), parse_mode="HTML")

@router.message(CategoryState.waiting_for_slug)
async def cat_add_slug(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all("admin_btn_cancel"):
        await state.clear()
        await message.answer(I18N.get(AdminKeys.CANCELLED, lang),
                             reply_markup=get_main_menu_keyboard(lang, True))
        return

    slug = message.text.strip().lower().replace(" ", "_")
    if not slug.replace("_", "").isalnum():
        await message.answer(I18N.get("admin_cat_slug_invalid", lang))
        return

    cat_service = CategoryService(session)
    existing = await cat_service.get_by_slug(slug)
    if existing:
        await message.answer(
            I18N.get("admin_cat_slug_exists", lang).format(slug=slug),
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    cat = await cat_service.create(slug=slug, name_uz=data["name_uz"], name_ru=data["name_ru"])
    await state.clear()
    await message.answer(
        I18N.get("admin_cat_added", lang).format(
            name_uz=cat.name_uz, name_ru=cat.name_ru, slug=cat.slug
        ),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, True)
    )

# ──────────────────── DELETE FLOW ─────────────────────────────
@router.message(F.from_user.id.in_(CONFIG.admin_ids),
                F.text.in_(I18N.get_all(AdminKeys.CAT_DELETE)))
async def cat_delete_start(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    cat_service = CategoryService(session)
    cats = await cat_service.get_all()
    if not cats:
        await message.answer(I18N.get("admin_cat_none", lang))
        return
    await state.set_state(CategoryState.waiting_for_delete)
    await message.answer(
        I18N.get("admin_cat_delete_prompt", lang),
        parse_mode="HTML",
        reply_markup=_cat_list_keyboard(cats, lang)
    )

@router.message(CategoryState.waiting_for_delete)
async def cat_delete_confirm(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    if message.text in I18N.get_all("admin_btn_cancel"):
        await state.clear()
        await message.answer(I18N.get(AdminKeys.CANCELLED, lang),
                             reply_markup=get_main_menu_keyboard(lang, True))
        return

    cat_service = CategoryService(session)
    cats = await cat_service.get_all()
    target = next((c for c in cats if c.name_uz == message.text), None)
    if not target:
        await message.answer(I18N.get("admin_cat_not_found", lang))
        return

    await cat_service.delete(target.id)
    await state.clear()
    await message.answer(
        I18N.get("admin_cat_deleted", lang).format(name=target.name_uz),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, True)
    )
