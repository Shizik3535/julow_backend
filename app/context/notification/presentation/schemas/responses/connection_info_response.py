from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ConnectionInfoResponse(BaseModel):
    """Ответ с информацией о подключении к real-time уведомлениям."""

    model_config = ConfigDict(from_attributes=True)

    websocket_url: str = Field(
        description="URL WebSocket-эндпоинта для подключения",
        examples=["wss://api.julow.com:8000/api/v1/ws/notifications"],
    )
    auth_method: str = Field(
        default="query",
        description="Способ передачи JWT-токена при подключении",
        examples=["query"],
    )
    auth_param: str = Field(
        default="token",
        description="Имя параметра для JWT-токена",
        examples=["token"],
    )
    heartbeat_interval_sec: int = Field(
        default=30,
        description="Рекомендуемый интервал heartbeat в секундах",
        examples=[30],
    )
    server_events: list[str] = Field(
        default_factory=list,
        description="Типы событий, отправляемых сервером через WebSocket",
        examples=[["notification.created", "notification.read"]],
    )
    client_messages: list[str] = Field(
        default_factory=list,
        description="Сообщения, принимаемые от клиента через WebSocket",
        examples=[["ping"]],
    )
