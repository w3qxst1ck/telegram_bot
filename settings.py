import os

from pydantic_settings import BaseSettings
from pydantic import Field


PRICES = {
    "1": 150,
    "3": 450,
    "6": 900,
    "12": 1800
}

STARS_PRICES = {
    "75": 150,
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
    bot_name: str = "VIRA Bot"
    bot_tg_name: str = "VIRADigitalBot"
    bot_token: str = Field(..., env='BOT_TOKEN')
    admins: list = Field(..., env='ADMINS')
    payment_admin: str = Field(..., env='PAYMENT_ADMIN')
    help_admin: str = Field(..., env='HELP_ADMIN')
    bank_phone: str = Field(..., env='BANK_PHONE')
    card_name: str = Field(..., env='CARD_NAME')

    timezone: str = "Europe/Moscow"

    trial_days: int = 7
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

