import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from services.user_service import UserService

class BroadcastService:
    def __init__(self, bot: Bot, session_pool):
        self.bot = bot
        self.session_pool = session_pool # async_sessionmaker

    async def send_to_all(self, from_chat_id: int, message_id: int):
        async with self.session_pool() as session:
            user_service = UserService(session)
            users = await user_service.get_all(only_active=True)
        
        success, blocked, error = 0, 0, 0
        
        for user in users:
            try:
                await self.bot.copy_message(
                    chat_id=user.telegram_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id
                )
                success += 1
                await asyncio.sleep(0.05) # Rate limiting
            except TelegramForbiddenError:
                blocked += 1
                async with self.session_pool() as session:
                    await UserService(session).update_status(user.telegram_id, False)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                # Retry once
                try:
                    await self.bot.copy_message(user.telegram_id, from_chat_id, message_id)
                    success += 1
                except:
                    error += 1
            except Exception as e:
                logging.error(f"Broadcast error for {user.telegram_id}: {e}")
                error += 1
        
        return success, blocked, error

    def start_broadcast(self, from_chat_id: int, message_id: int, callback=None):
        """Fon rejimida (background) xabar yuborishni boshlaydi."""
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_to_all(from_chat_id, message_id))
        if callback:
            task.add_done_callback(lambda t: asyncio.create_task(callback(t.result())))
        return task
