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


settings = Settings()
