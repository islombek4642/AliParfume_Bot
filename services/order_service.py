from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from database.models import Order, User, OrderItem, Product
from typing import List, Optional, Tuple
from services.base_service import BaseService

class OrderService(BaseService):
    async def create(self, user_id: int, cart_items: list, total_price: float, address: str = None) -> Order:
        """
        Creates an Order and associated OrderItems.
        cart_items should be a list of CartItem models.
        """
        order = Order(user_id=user_id, total_price=total_price, address=address)
        self.session.add(order)
        await self.session.flush() # Get order.id

        for item in cart_items:
            # We need product names and current prices for history
            product = item.product
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                name=product.name_uz, # Defaulting to UZ for history, or we could store both
                quantity=item.quantity,
                price=product.price
            )
            self.session.add(order_item)
        
        await self.commit()
        return order

    async def get_user_orders(self, user_id: int) -> List[Order]:
        query = select(Order).where(Order.user_id == user_id).options(selectinload(Order.items)).order_by(Order.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        query = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        query = update(Order).where(Order.id == order_id).values(status=new_status)
        await self.session.execute(query)
        await self.commit()
        return await self.get_by_id(order_id)

    async def get_stats(self) -> Tuple[int, int, float]:
        user_count = (await self.session.execute(select(func.count(User.id)))).scalar()
        order_count = (await self.session.execute(select(func.count(Order.id)))).scalar()
        total_sales = (await self.session.execute(select(func.sum(Order.total_price)))).scalar() or 0
        return user_count, order_count, total_sales
