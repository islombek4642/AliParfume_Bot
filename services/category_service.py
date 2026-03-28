from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Category, Product
from typing import List, Optional

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Category]:
        query = select(Category)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.session.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, slug: str, name_uz: str, name_ru: str) -> Category:
        cat = Category(slug=slug, name_uz=name_uz, name_ru=name_ru)
        self.session.add(cat)
        await self.session.commit()
        return cat

    async def delete(self, category_id: int) -> None:
        # Delete all products in this category first (cascade)
        await self.session.execute(delete(Product).where(Product.category_id == category_id))
        await self.session.execute(delete(Category).where(Category.id == category_id))
        await self.session.commit()
