import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: Union[int, str]
    CHANNEL_ID: int

    @property
    def admin_ids(self) -> List[int]:
        if isinstance(self.ADMIN_ID, int):
            return [self.ADMIN_ID]
        try:
            return [int(x.strip()) for x in str(self.ADMIN_ID).split(",") if x.strip()]
        except ValueError:
            return []

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids

    DB_USER: str = "aliparfume_user"
    DB_PASS: str = "aliparfume_pass"
    DB_NAME: str = "aliparfume_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # DB Pooling
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Global settings instance
CONFIG = Settings()

# Categories (Constants as requested)
class Categories:
    PERFUME = "perfume"
    COSMETIC = "cosmetic"
    OTHER = "other"

    ALL = [PERFUME, COSMETIC, OTHER]

# Order Statuses
class OrderStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
