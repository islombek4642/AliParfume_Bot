from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Product, Category
from typing import List, Optional

class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, category_id: int | None = None, in_stock_only: bool = True) -> List[Product]:
        query = select(Product).order_by(Product.id)
        if category_id:
            query = query.where(Product.category_id == category_id)
        if in_stock_only:
            query = query.where(Product.stock > 0)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, category_id: int, name_uz: str, name_ru: str, price: float, desc_uz: str, desc_ru: str, photo_id: str, stock: int = 0) -> Product:
        product = Product(
            category_id=category_id,
            name_uz=name_uz,
            name_ru=name_ru,
            price=price,
            description_uz=desc_uz,
            description_ru=desc_ru,
            photo_id=photo_id,
            stock=stock
        )
        self.session.add(product)
        await self.session.commit()
        return product

    async def delete(self, product_id: int):
        query = delete(Product).where(Product.id == product_id)
        await self.session.execute(query)
        await self.session.commit()

    async def update_price(self, product_id: int, new_price: float):
        query = update(Product).where(Product.id == product_id).values(price=new_price)
        await self.session.execute(query)
        await self.session.commit()

    async def search_by_name(self, name: str) -> Optional[Product]:
        query = select(Product).where(or_(Product.name_uz == name, Product.name_ru == name))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def update_stock(self, product_id: int, quantity_change: int):
        query = update(Product).where(Product.id == product_id).values(stock=Product.stock + quantity_change)
        await self.session.execute(query)
        await self.session.commit()
