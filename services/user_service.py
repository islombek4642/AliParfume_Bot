from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from typing import Optional, List

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, full_name: str, language: str = "uz") -> User:
        user = User(telegram_id=telegram_id, full_name=full_name, language=language)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_language(self, telegram_id: int, language: str):
        query = update(User).where(User.telegram_id == telegram_id).values(language=language)
        await self.session.execute(query)
        await self.session.commit()

    async def get_all(self, only_active: bool = True) -> List[User]:
        query = select(User)
        if only_active:
            query = query.where(User.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(self, telegram_id: int, is_active: bool):
        query = update(User).where(User.telegram_id == telegram_id).values(is_active=is_active)
        await self.session.execute(query)
        await self.session.commit()

    async def add_to_cart(self, telegram_id: int, product_id: int, quantity: int):
        user = await self.get_by_id(telegram_id)
        if user:
            cart = dict(user.cart) if user.cart else {}
            product_id_str = str(product_id)
            if product_id_str in cart:
                cart[product_id_str] += quantity
            else:
                cart[product_id_str] = quantity
            
            query = update(User).where(User.telegram_id == telegram_id).values(cart=cart)
            await self.session.execute(query)
            await self.session.commit()

    async def clear_cart(self, telegram_id: int):
        query = update(User).where(User.telegram_id == telegram_id).values(cart={})
        await self.session.execute(query)
        await self.session.commit()

    async def delete_from_cart(self, telegram_id: int, product_id: int):
        user = await self.get_by_id(telegram_id)
        if user and user.cart:
            cart = dict(user.cart)
            product_id_str = str(product_id)
            if product_id_str in cart:
                del cart[product_id_str]
                query = update(User).where(User.telegram_id == telegram_id).values(cart=cart)
                await self.session.execute(query)
                await self.session.commit()
