from pydantic_settings import BaseSettings, SettingsConfigDict


class LiveKitSettings(BaseSettings):
    """Настройки подключения к LiveKit SFU-серверу.

    Переменные окружения (с префиксом ``LIVEKIT_``):
        LIVEKIT_URL: HTTP-адрес LiveKit внутри docker-сети (для генерации токенов).
        LIVEKIT_API_KEY: API-ключ из ``livekit.yaml`` / ``keys``.
        LIVEKIT_API_SECRET: Секрет, парный к API-ключу.
        LIVEKIT_PUBLIC_URL: WebSocket URL, который получит браузер клиента
            (``ws://`` для dev, ``wss://`` для production).
    """

    model_config = SettingsConfigDict(
        env_prefix="LIVEKIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "http://localhost:7880"
    api_key: str = "devkey"
    api_secret: str = "secret1234567890secret1234567890"
    public_url: str = "ws://localhost:7880"
