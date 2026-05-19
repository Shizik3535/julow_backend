from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    endpoint_url: str = "http://localhost:9000"
    public_endpoint_url: str = ""
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket_name: str = "julow"
    region: str = "us-east-1"
    presigned_url_expires: int = 3600
