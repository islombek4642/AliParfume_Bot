from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession
from database.requests import get_user
from utils.localization import I18N

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        db_user = await get_user(session, user.id)
        
        lang = db_user.language if db_user else "uz"
        
        # Inject translation function and current language into data
        data["_"] = lambda key: I18N.get(key, lang)
        data["lang"] = lang
        
        return await handler(event, data)
