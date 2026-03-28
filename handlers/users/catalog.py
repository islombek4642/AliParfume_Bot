from aiogram import Router, F, types
from aiogram.types import Message
from services.product_service import ProductService
from services.category_service import CategoryService
from keyboards.reply import get_categories_keyboard, get_main_menu_keyboard, get_products_keyboard
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

        await message.answer(_("catalog_header"), reply_markup=get_products_keyboard(lang, products))
        
        for product in products:
            name = product.name_uz if lang == "uz" else product.name_ru
            desc = product.description_uz if lang == "uz" else product.description_ru
            
            caption = (
                f"<b>{name}</b>\n\n"
                f"<i>{_('product_desc')}{desc}</i>\n"
                f"<b>{_('product_price')}{product.price:,} so'm</b>"
            )
            
            if product.photo_id:
                await message.answer_photo(product.photo_id, caption=caption, parse_mode="HTML")
            else:
                await message.answer(caption, parse_mode="HTML")
