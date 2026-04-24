from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OAUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
