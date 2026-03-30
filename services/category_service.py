from sqlalchemy import select, delete
from database.models import Category, Product
from typing import List, Optional
from services.base_service import BaseService

class CategoryService(BaseService):
    async def get_all(self) -> List[Category]:
        query = select(Category)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        query = select(Category).where(Category.id == category_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        query = select(Category).where(Category.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, slug: str, name_uz: str, name_ru: str) -> Category:
        category = Category(slug=slug, name_uz=name_uz, name_ru=name_ru)
        self.session.add(category)
        await self.commit()
        return category

    async def delete(self, category_id: int) -> None:
        await self.session.execute(delete(Product).where(Product.category_id == category_id))
        await self.session.execute(delete(Category).where(Category.id == category_id))
        await self.commit()
