import os

from pydantic_settings import BaseSettings
from pydantic import Field


PRICES = {
    "1": 100,
    "3": 300,
    "6": 600,
    "12": 1200
}


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


class Server(BaseSettings):
    username: str = Field(..., env='HOSTNAME')
    password: str = Field(..., env='PASSWORD')
    flow: str = "xtls-rprx-vision"


class Settings(BaseSettings):
    bot_name: str = "VLESS VPN bot"
    bot_token: str = Field(..., env='BOT_TOKEN')
    admins: list = Field(..., env='ADMINS')
    timezone: str = "Europe/Moscow"
    trial_days: int = 1

    price_list: dict = PRICES

    db: Database = Database()
    redis: Redis = Redis()
    server: Server = Server()


settings = Settings()

