from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order, User
from typing import List, Tuple

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, items: dict, total_price: float, address: str = None) -> Order:
        order = Order(user_id=user_id, items=items, total_price=total_price, address=address)
        self.session.add(order)
        await self.session.commit()
        return order

    async def get_user_orders(self, user_id: int) -> List[Order]:
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_stats(self) -> Tuple[int, int, float]:
        user_count = (await self.session.execute(select(func.count(User.id)))).scalar()
        order_count = (await self.session.execute(select(func.count(Order.id)))).scalar()
        total_sales = (await self.session.execute(select(func.sum(Order.total_price)))).scalar() or 0
        return user_count, order_count, total_sales
