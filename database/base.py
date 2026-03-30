from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from data.config import CONFIG

engine = create_async_engine(
    CONFIG.database_url, 
    echo=False, 
    pool_size=CONFIG.DB_POOL_SIZE, 
    max_overflow=CONFIG.DB_MAX_OVERFLOW
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def init_db():
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Migration: Ensure columns exist
        migrations = [
            ("users", "full_name", "VARCHAR(255)"),
            ("users", "phone", "VARCHAR(20)"),
            ("users", "is_admin", "BOOLEAN DEFAULT FALSE"),
            ("users", "is_active", "BOOLEAN DEFAULT TRUE"),
            ("users", "language", "VARCHAR(5) DEFAULT 'uz'"),
            ("products", "stock", "INTEGER DEFAULT 0"),
        ]
        
        for table, column, column_def in migrations:
            try:
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {column_def}"))
            except Exception:
                pass
