from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexusOne"
    database_url: str = "sqlite:///./data/nexusone.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "replace-with-a-long-random-secret-at-least-32"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:3005"
    app_seed_password: str = "ChangeMe123!"
    seed_demo_data: bool = True
    redis_optional: bool = True
    worker_interval_seconds: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
