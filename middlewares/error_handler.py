import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logging.error(f"Critical error in handler: {e}", exc_info=True)
            # You can inform the user here if needed
            if hasattr(event, "message") and event.message:
                await event.message.answer("⚠️ Kechirasiz, texnik xatolik yuz berdi. Tezi orada tuzatamiz.")
            elif hasattr(event, "callback_query") and event.callback_query:
                await event.callback_query.answer("⚠️ Texnik xatolik!", show_alert=True)
            return None
