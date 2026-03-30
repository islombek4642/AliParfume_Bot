from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from services.export_service import ExportService
from database.base import AsyncSessionLocal
from data.config import CONFIG
from aiogram.types import BufferedInputFile
import logging

async def send_weekly_report(bot: Bot):
    logging.info("Generating weekly automated report...")
    async with AsyncSessionLocal() as session:
        export_service = ExportService(session)
        # We can send both Users and Orders
        try:
            users_file = await export_service.export_users_to_excel()
            orders_file = await export_service.export_orders_to_excel()
            
            for admin_id in CONFIG.admin_ids:
                try:
                    await bot.send_document(
                        admin_id, 
                        BufferedInputFile(users_file.read(), filename="weekly_users.xlsx"),
                        caption="📊 Haftalik avtomatik hisobot: Foydalanuvchilar"
                    )
                    users_file.seek(0)
                    await bot.send_document(
                        admin_id, 
                        BufferedInputFile(orders_file.read(), filename="weekly_orders.xlsx"),
                        caption="💰 Haftalik avtomatik hisobot: Buyurtmalar"
                    )
                    orders_file.seek(0)
                except Exception as e:
                    logging.error(f"Failed to send report to {admin_id}: {e}")
        except Exception as e:
            logging.error(f"Error generating weekly report: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    # Every Monday at 09:00
    scheduler.add_job(send_weekly_report, "cron", day_of_week="mon", hour=9, minute=0, args=[bot])
    # Also a daily "Alive" check or simple backup logic could go here
    return scheduler
