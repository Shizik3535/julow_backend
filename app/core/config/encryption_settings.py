from pydantic_settings import BaseSettings, SettingsConfigDict


class EncryptionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ENCRYPTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    key: str = "change-me-in-production-base64-fernet-key=="
