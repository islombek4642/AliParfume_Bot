from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from database.models import CartItem, User
from services.base_service import BaseService
from typing import List

class CartService(BaseService):
    async def get_items(self, user_id: int) -> List[CartItem]:
        query = select(CartItem).where(CartItem.user_id == user_id).options(selectinload(CartItem.product))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_item(self, user_id: int, product_id: int, quantity: int = 1):
        # Check if item already in cart
        query = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        )
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
        else:
            item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            self.session.add(item)
        
        await self.commit()

    async def remove_item(self, user_id: int, product_id: int):
        query = delete(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        )
        await self.session.execute(query)
        await self.commit()

    async def clear_cart(self, user_id: int):
        query = delete(CartItem).where(CartItem.user_id == user_id)
        await self.session.execute(query)
        await self.commit()

    async def get_cart_total(self, user_id: int) -> float:
        items = await self.get_items(user_id)
        total = 0
        from services.product_service import ProductService
        prod_service = ProductService(self.session)
        for item in items:
            product = await prod_service.get_by_id(item.product_id)
            if product:
                total += product.price * item.quantity
        return total
