from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Category, Product, Order
from typing import List, Optional

async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, telegram_id: int, full_name: str, language: str = "uz") -> User:
    user = User(telegram_id=telegram_id, full_name=full_name, language=language)
    session.add(user)
    await session.commit()
    return user

async def update_user_language(session: AsyncSession, telegram_id: int, language: str):
    query = update(User).where(User.telegram_id == telegram_id).values(language=language)
    await session.execute(query)
    await session.commit()

async def get_categories(session: AsyncSession) -> List[Category]:
    query = select(Category)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_products_by_category(session: AsyncSession, category_id: int) -> List[Product]:
    query = select(Product).where(Product.category_id == category_id)
    result = await session.execute(query)
    return list(result.scalars().all())

async def add_to_cart(session: AsyncSession, telegram_id: int, product_id: int, quantity: int):
    user = await get_user(session, telegram_id)
    if user:
        cart = dict(user.cart) if user.cart else {}
        product_id_str = str(product_id)
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity
        
        query = update(User).where(User.telegram_id == telegram_id).values(cart=cart)
        await session.execute(query)
        await session.commit()

async def clear_cart(session: AsyncSession, telegram_id: int):
    query = update(User).where(User.telegram_id == telegram_id).values(cart={})
    await session.execute(query)
    await session.commit()

async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def add_order(session: AsyncSession, user_id: int, items: dict, total_price: float, address: str = None) -> Order:
    order = Order(user_id=user_id, items=items, total_price=total_price, address=address)
    session.add(order)
    await session.commit()
    return order

async def get_user_orders(session: AsyncSession, user_id: int) -> List[Order]:
    query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_all_users(session: AsyncSession) -> List[User]:
    query = select(User)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_stats(session: AsyncSession):
    from sqlalchemy import func
    user_count = (await session.execute(select(func.count(User.id)))).scalar()
    order_count = (await session.execute(select(func.count(Order.id)))).scalar()
    total_sales = (await session.execute(select(func.sum(Order.total_price)))).scalar() or 0
    return user_count, order_count, total_sales

async def add_product(session: AsyncSession, category_id: int, name_uz: str, name_ru: str, price: float, desc_uz: str, desc_ru: str, photo_id: str) -> Product:
    product = Product(category_id=category_id, name_uz=name_uz, name_ru=name_ru, price=price, description_uz=desc_uz, description_ru=desc_ru, photo_id=photo_id)
    session.add(product)
    await session.commit()
    return product

async def delete_from_cart(session: AsyncSession, telegram_id: int, product_id: int):
    user = await get_user(session, telegram_id)
    if user and user.cart:
        cart = dict(user.cart)
        product_id_str = str(product_id)
        if product_id_str in cart:
            del cart[product_id_str]
            query = update(User).where(User.telegram_id == telegram_id).values(cart=cart)
            await session.execute(query)
            await session.commit()
