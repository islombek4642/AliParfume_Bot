import asyncio
from database.base import AsyncSessionLocal, init_db
from database.models import Category
from data.config import Categories
from sqlalchemy import select

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if categories already exist
        result = await session.execute(select(Category))
        if result.scalars().first():
            print("Categories already exist!")
            return

        print("Seeding initial categories...")
        categories = [
            Category(slug=Categories.PERFUME, name_uz="Atirlar", name_ru="Парфюмерия"),
            Category(slug=Categories.COSMETIC, name_uz="Kosmetika", name_ru="Косметика"),
            Category(slug=Categories.OTHER, name_uz="Boshqalar", name_ru="Прочее"),
        ]
        session.add_all(categories)
        await session.commit()
        
        # Add sample products
        from database.models import Product
        
        # Get category IDs
        perfume_cat = (await session.execute(select(Category).where(Category.slug == Categories.PERFUME))).scalar_one()
        cosmetic_cat = (await session.execute(select(Category).where(Category.slug == Categories.COSMETIC))).scalar_one()
        
        products = [
            Product(category_id=perfume_cat.id, name_uz="Sauvage Dior", name_ru="Sauvage Dior", 
                    description_uz="Erkaklar uchun klassik atir.", description_ru="Классический мужской парфюм.", price=1200000),
            Product(category_id=perfume_cat.id, name_uz="Chanel No.5", name_ru="Chanel No.5", 
                    description_uz="Ayollar uchun afsonaviy atir.", description_ru="Легендарный женский парфюм.", price=1500000),
            Product(category_id=cosmetic_cat.id, name_uz="Loreal Max", name_ru="Loreal Max", 
                    description_uz="Sifatli yuz kremi.", description_ru="Качественный крем для лица.", price=350000),
        ]
        session.add_all(products)
        await session.commit()
        print("Initial categories and products added successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
