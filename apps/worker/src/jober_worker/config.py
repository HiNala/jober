from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    database_url: str = "postgresql+psycopg://jober:jober@localhost:5432/jober"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "jober-artifacts"
    minio_secure: bool = False
    vault_encryption_key: str = ""
    playwright_headed: bool = True
    playwright_slow_mo_ms: int = 0
    browserless_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    batch_tick_seconds: int = 5
    celery_worker_concurrency: int = 2

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> str:
        if isinstance(value, str):
            if value.startswith("postgresql+asyncpg://"):
                return value.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
            if value.startswith("postgresql://"):
                return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value  # type: ignore[return-value]


settings = Settings()
