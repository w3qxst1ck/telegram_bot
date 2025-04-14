import os

from pydantic_settings import BaseSettings
from pydantic import Field


PRICES = {
    "1": 100,
    "3": 300,
    "6": 600,
    "12": 1200
}

STARS_PRICES = {
    "50": 100,
    "150": 300,
    "300": 600,
    "600": 1200
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
    username: str = Field(..., env='USERNAME')
    password: str = Field(..., env='PASSWORD')
    flow: str = "xtls-rprx-vision"


class Settings(BaseSettings):
    bot_name: str = "VLESS VPN bot"
    bot_tg_name: str = "VlessDigitalBot"
    bot_token: str = Field(..., env='BOT_TOKEN')
    admins: list = Field(..., env='ADMINS')
    payment_admin: str = Field(..., env='PAYMENT_ADMIN')
    help_admin: str = Field(..., env='HELP_ADMIN')

    timezone: str = "Europe/Moscow"

    trial_days: int = 1
    price_list: dict = PRICES
    stars_price_list: dict = STARS_PRICES
    traffic_limit: int = 100
    extra_traffic_price: int = 100
    extra_traffic_size: int = 100
    paid_period: int = 30
    ref_bonus: int = 100

    db: Database = Database()
    redis: Redis = Redis()
    server: Server = Server()

    need_payment_service: bool = False
    payment_token: str = Field(..., env='PAYMENT_TOKEN')

    user_agreement_link: str = "https://telegra.ph/PUBLICHNAYA-OFERTA-04-08-2"


settings = Settings()

