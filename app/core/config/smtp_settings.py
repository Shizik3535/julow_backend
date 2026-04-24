from pydantic_settings import BaseSettings, SettingsConfigDict


class SmtpSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SMTP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 587
    username: str = ""
    password: str = ""
    use_tls: bool = True
    from_email: str = "noreply@julow.com"
