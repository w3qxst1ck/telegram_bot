from pydantic_settings import BaseSettings, SettingsConfigDict


class Database(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")


class Settings(BaseSettings):
    bot_token: str
    admins: list
    db: Database = Database()
    timezone: str = "Europe/Moscow"

    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")


settings = Settings()

