from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Category
from typing import List

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Category]:
        query = select(Category)
        result = await self.session.execute(query)
        return list(result.scalars().all())
