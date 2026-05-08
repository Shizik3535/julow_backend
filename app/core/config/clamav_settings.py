from pydantic_settings import BaseSettings, SettingsConfigDict


class ClamAvSettings(BaseSettings):
    """
    Настройки ClamAV-сканера.

    `enabled=False` → используется ``NoOpScannerAdapter`` (всегда clean) —
    подходит для тестов и быстрой разработки. В production задайте
    `CLAMAV_ENABLED=true` и поднимите контейнер `clamav/clamav`.

    `block_pending_downloads=True` блокирует скачивание файлов со статусом
    ``PENDING`` (сканирование ещё не завершено). По умолчанию включено
    для безопасности.
    """

    model_config = SettingsConfigDict(
        env_prefix="CLAMAV_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = False
    host: str = "localhost"
    port: int = 3310
    # Таймаут на одно сканирование (секунды).
    timeout_seconds: float = 60.0
    # Максимальный размер передаваемого чанка (по умолчанию clamd: 25 MiB).
    chunk_size_bytes: int = 1024 * 1024
    block_pending_downloads: bool = True
