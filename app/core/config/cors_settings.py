from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    allowed_origins: list[str] = ["*"]
    allow_credentials: bool = False
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["*"]
