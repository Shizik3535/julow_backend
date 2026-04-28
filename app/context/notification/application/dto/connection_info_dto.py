from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class ConnectionInfoDTO(BaseDTO):
    """
    DTO информации о подключении к real-time уведомлениям.

    Атрибуты:
        websocket_url: URL WebSocket-эндпоинта.
        auth_method: Способ передачи токена (query, header).
        auth_param: Имя параметра для токена.
        heartbeat_interval_sec: Интервал heartbeat в секундах.
        server_events: Типы событий, отправляемых сервером.
        client_messages: Сообщения, принимаемые от клиента.
    """

    websocket_url: str
    auth_method: str = "query"
    auth_param: str = "token"
    heartbeat_interval_sec: int = 30
    server_events: list[str] = []
    client_messages: list[str] = []
