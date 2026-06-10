from typing import Annotated

from pydantic import BeforeValidator, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _split_csv(value: object) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return value
    return []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "jober-artifacts"
    minio_secure: bool = False
    minio_region: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: Annotated[
        list[str],
        NoDecode,
        BeforeValidator(_split_csv),
    ] = ["http://localhost:3000", "http://127.0.0.1:3000"]
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
    auth_mode: str = "dev"
    dev_auth_bypass: bool = False
    clerk_jwt_issuer: str = ""
    clerk_jwt_secret: str = ""
    session_cookie_name: str = "jober_session"
    refresh_cookie_name: str = "jober_refresh"
    csrf_cookie_name: str = "jober_csrf"
    session_ttl_seconds: int = 86_400
    refresh_ttl_seconds: int = 604_800
    cookie_secure: bool = False
    auth_rate_limit_max: int = 20
    auth_rate_limit_window_seconds: int = 300
    auth_lockout_threshold: int = 5
    auth_lockout_seconds: int = 900
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro_monthly: str = ""
    browserless_url: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    oauth_state_ttl_seconds: int = 600
    web_app_url: str = "http://localhost:3000"
    analytics_enabled: bool = True
    analytics_session_timeout_minutes: int = 30
    analytics_anon_rotation_days: int = 30
    analytics_internal_user_ids: str = ""
    analytics_retention_days: int = 365
    run_artifact_retention_days: int = 90
    admin_bootstrap_secret: str = ""

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> str:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value  # type: ignore[return-value]

    @field_validator("minio_endpoint", mode="before")
    @classmethod
    def normalize_minio_endpoint(cls, value: object) -> str:
        if isinstance(value, str):
            return value.removeprefix("https://").removeprefix("http://")
        return value  # type: ignore[return-value]

settings = Settings()
