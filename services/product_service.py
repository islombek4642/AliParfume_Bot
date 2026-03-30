from sqlalchemy import select, update, delete, or_
from database.models import Product
from typing import List, Optional
from services.base_service import BaseService

class ProductService(BaseService):
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, category_id: int | None = None, in_stock_only: bool = False) -> List[Product]:
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
        await self.commit()
        return product

    async def update_stock(self, product_id: int, quantity_change: int):
        product = await self.get_by_id(product_id)
        if product:
            product.stock += quantity_change
            await self.commit()

    async def search_products(self, query: str) -> List[Product]:
        stmt = select(Product).where(
            (Product.name_uz.ilike(f"%{query}%")) | 
            (Product.name_ru.ilike(f"%{query}%"))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        query = update(Product).where(Product.id == product_id).values(**kwargs)
        await self.session.execute(query)
        await self.commit()
        return await self.get_by_id(product_id)

    async def delete(self, product_id: int):
        query = delete(Product).where(Product.id == product_id)
        await self.session.execute(query)
        await self.commit()
