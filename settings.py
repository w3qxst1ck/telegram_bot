import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Database(BaseSettings):
    postgres_user: str = Field(..., env='POSTGRES_USER')
    postgres_password: str = Field(..., env='POSTGRES_USER')
    postgres_db: str = Field(..., env='POSTGRES_DB')
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: str = Field(..., env='POSTGRES_PORT')

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


class Redis(BaseSettings):
    redis_port: str = "6379"
    redis_password: str = Field(..., env='REDIS_PASSWORD')


class Settings(BaseSettings):
    bot_token: str = Field(..., env='BOT_TOKEN')
    bot_name: str = "Vless VPN bot"
    admins: list = Field(..., env='ADMINS')
    db: Database = Database()
    redis: Redis = Redis()
    timezone: str = "Europe/Moscow"
    trial_days: int = 1
    price: int = 200
    servers: dict = {
        "am-1": {
            "url": "https://somedomain123.store:2053/jA7PFJItw5/",
            "hostname": "admin",
            "password": "Dn39xe53MpZ2",
            "domain": "somedomain123.store",
            "flow": "xtls-rprx-vision",
        }
    }


settings = Settings()

