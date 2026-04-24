from pydantic_settings import BaseSettings, SettingsConfigDict


class NtfySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NTFY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = "https://ntfy.sh"
    default_topic: str = "julow"
