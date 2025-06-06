from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str | None = None

    # Application
    app_name: str = "Work Order API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Security
    secret_key: str = "your-secret-key-here"  # Change in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
