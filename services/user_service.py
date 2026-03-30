from sqlalchemy import select, update
from database.models import User
from typing import Optional, List
from services.base_service import BaseService

class UserService(BaseService):
    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, full_name: str, language: str = "uz", is_admin: bool = False) -> User:
        user = User(telegram_id=telegram_id, full_name=full_name, language=language, is_admin=is_admin)
        self.session.add(user)
        await self.commit()
        return user

    async def update_language(self, telegram_id: int, language: str):
        query = update(User).where(User.telegram_id == telegram_id).values(language=language)
        await self.session.execute(query)
        await self.commit()

    async def get_all(self, only_active: bool = True) -> List[User]:
        query = select(User)
        if only_active:
            query = query.where(User.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(self, telegram_id: int, is_active: bool):
        query = update(User).where(User.telegram_id == telegram_id).values(is_active=is_active)
        await self.session.execute(query)
        await self.commit()

    async def update_phone(self, telegram_id: int, phone: str):
        query = update(User).where(User.telegram_id == telegram_id).values(phone=phone)
        await self.session.execute(query)
        await self.commit()

    async def set_admin(self, telegram_id: int, is_admin: bool):
        query = update(User).where(User.telegram_id == telegram_id).values(is_admin=is_admin)
        await self.session.execute(query)
        await self.commit()
