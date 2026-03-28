import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import CONFIG
from database.base import init_db, AsyncSessionLocal
from handlers.users import start, catalog, cart
from handlers.admin import panel, utils, products, orders_admin, categories
from middlewares.db_middleware import DbSessionMiddleware
from middlewares.i18n_middleware import I18nMiddleware
from aiogram.types import BotCommand, BotCommandScopeDefault
from utils.timezone import TZ_UZBEKISTAN, get_now_aware

def uz_time_converter(*args):
    return get_now_aware().timetuple()

logging.Formatter.converter = uz_time_converter

async def set_bot_commands(bot: Bot):
    commands_uz = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="about", description="Biz haqimizda"),
        BotCommand(command="settings", description="Tilni tanlash")
    ]
    commands_ru = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="about", description="О нас"),
        BotCommand(command="settings", description="Выбор языка")
    ]
    
    await bot.set_my_commands(commands_uz, scope=BotCommandScopeDefault(), language_code="uz")
    await bot.set_my_commands(commands_ru, scope=BotCommandScopeDefault(), language_code="ru")
    await bot.set_my_commands(commands_uz, scope=BotCommandScopeDefault()) # Default

async def main():
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )

    # Initialize Bot and Dispatcher
    bot = Bot(token=CONFIG.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Initialize Database
    await init_db()

    # Set Bot Commands
    await set_bot_commands(bot)

    # Register Middlewares
    dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.middleware(I18nMiddleware())

    # Register Routers (Ordered by priority)
    dp.include_router(panel.router)
    dp.include_router(products.router)
    dp.include_router(categories.router)
    dp.include_router(orders_admin.router)
    dp.include_router(cart.router)
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(utils.router)

    # Start Polling
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
