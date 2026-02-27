from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://friend:friend@db:5432/friend"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24時間
    algorithm: str = "HS256"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
