from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "jober-artifacts"
    minio_secure: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    secret_key: str = ""
    vault_encryption_key: str = ""
    llm_api_key: str = ""
    llm_provider: str = "openai"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_draft_model: str = "gpt-4o-mini"
    llm_scoring_model: str = "gpt-4o-mini"
    llm_embedding_model: str = "text-embedding-3-small"
    llm_monthly_budget_usd: float = 25.0
    llm_budget_soft_warn_ratio: float = 0.8
    batch_max_concurrency: int = 1
    batch_site_cooldown_seconds: float = 30.0
    batch_action_delay_ms: int = 500
    batch_tick_seconds: int = 5
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    quiet_hours_timezone: str = "UTC"
    auto_submit_opt_in: bool = False
    jober_env: str = "development"
    log_mode: str = "redacted"
    presigned_url_ttl_minutes: int = 15
    require_secrets: bool = False


settings = Settings()
