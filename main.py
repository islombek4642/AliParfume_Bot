import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from data.config import CONFIG
from database.base import init_db, AsyncSessionLocal
from handlers.users import start, catalog, cart, history
from handlers.admin import panel, utils, products, orders_admin, categories
from middlewares.db_middleware import DbSessionMiddleware
from middlewares.i18n_middleware import I18nMiddleware
from middlewares.error_handler import ErrorHandlerMiddleware
from aiogram.types import BotCommand, BotCommandScopeDefault
from utils.timezone import TZ_UZBEKISTAN, get_now_aware
from utils.logger import setup_logger
from utils.scheduler import setup_scheduler

# Setup Logger
setup_logger()

# ... (uz_time_converter remains same)

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=CONFIG.BOT_TOKEN)
    
    # Redis Storage
    redis = Redis.from_url(CONFIG.redis_url)
    storage = RedisStorage(redis)
    dp = Dispatcher(storage=storage)

    # Initialize Database
    await init_db()

    # Setup Scheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()

    # Register Middlewares
    dp.update.middleware(ErrorHandlerMiddleware())
    dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.middleware(I18nMiddleware())

    # Register Routers (Ordered by priority)
    dp.include_router(panel.router)
    dp.include_router(products.router)
    dp.include_router(categories.router)
    dp.include_router(orders_admin.router)
    dp.include_router(cart.router)
    dp.include_router(history.router)
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
