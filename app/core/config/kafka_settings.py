from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bootstrap_servers: str = "localhost:9092"
    group_id: str = "julow-consumer"
    auto_offset_reset: str = "earliest"
