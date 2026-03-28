from aiogram import Router, F, types
from aiogram.types import Message
from services.product_service import ProductService
from services.category_service import CategoryService
from keyboards.reply import get_categories_keyboard, get_main_menu_keyboard
from keyboards.inline import get_product_inline_keyboard
from utils.localization import I18N
from data.constants import MenuKeys
from data.config import CONFIG
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.message(F.text.in_(I18N.get_all(MenuKeys.CATALOG)))
async def show_categories(message: Message, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await message.answer(
        _("catalog_header"),
        reply_markup=get_categories_keyboard(lang, categories)
    )

@router.message(F.text.in_(I18N.get_all(MenuKeys.BACK)))
@router.message(F.text.in_(I18N.get_all(MenuKeys.MAIN)))
async def go_main(message: Message, session: AsyncSession, _, lang):
    is_admin = CONFIG.is_admin(message.from_user.id)
    await message.answer(
        _("main_menu"),
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )

@router.message(F.text)
async def handle_category_selection(message: Message, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    product_service = ProductService(session)
    
    categories = await category_service.get_all()
    
    # Identify selected category by localized name
    selected_category = next(
        (cat for cat in categories if message.text == (cat.name_uz if lang == "uz" else cat.name_ru)),
        None
    )
    
    if selected_category:
        products = await product_service.get_all(selected_category.id)
        if not products:
            await message.answer(_("cart_empty")) 
            return

        # Show only the first product with inline pagination
        product = products[0]
        name = product.name_uz if lang == "uz" else product.name_ru
        desc = product.description_uz if lang == "uz" else product.description_ru
        caption = (
            f"<b>{name}</b>\n\n"
            f"<i>{_('product_desc')}{desc}</i>\n"
            f"<b>{_('product_price')}{product.price:,} so'm</b>"
        )
        
        reply_markup = get_product_inline_keyboard(lang, selected_category.id, 0, len(products), product.id)
        
        if product.photo_id:
            await message.answer_photo(product.photo_id, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await message.answer(caption, parse_mode="HTML", reply_markup=reply_markup)

@router.callback_query(F.data.startswith("prod_page:"))
async def handle_pagination(callback: types.CallbackQuery, session: AsyncSession, _, lang):
    prefix, category_id, index = callback.data.split(":")
    category_id, index = int(category_id), int(index)
    
    product_service = ProductService(session)
    products = await product_service.get_all(category_id)
    
    if index < 0 or index >= len(products):
        await callback.answer()
        return
        
    product = products[index]
    name = product.name_uz if lang == "uz" else product.name_ru
    desc = product.description_uz if lang == "uz" else product.description_ru
    caption = (
        f"<b>{name}</b>\n\n"
        f"<i>{_('product_desc')}{desc}</i>\n"
        f"<b>{_('product_price')}{product.price:,} so'm</b>"
    )
    
    reply_markup = get_product_inline_keyboard(lang, category_id, index, len(products), product.id)
    
    try:
        if product.photo_id:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(media=product.photo_id, caption=caption, parse_mode="HTML"),
                reply_markup=reply_markup
            )
        else:
            await callback.message.edit_text(text=caption, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        pass # Handle cases where message content hasn't changed
    
    await callback.answer()

@router.callback_query(F.data == "noop")
async def handle_noop(callback: types.CallbackQuery):
    await callback.answer()

@router.callback_query(F.data == "back_to_cats")
async def handle_back_to_cats(callback: types.CallbackQuery, session: AsyncSession, _, lang):
    category_service = CategoryService(session)
    categories = await category_service.get_all()
    await callback.message.delete()
    await callback.message.answer(
        _("catalog_header"),
        reply_markup=get_categories_keyboard(lang, categories)
    )
    await callback.answer()
