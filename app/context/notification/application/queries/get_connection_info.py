from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.notification.application.dto.connection_info_dto import ConnectionInfoDTO


class GetConnectionInfoQuery(BaseQuery):
    """
    Запрос информации о подключении к real-time уведомлениям.

    Атрибуты:
        user_id: ID пользователя (для будущего per-user URL).
    """

    user_id: str


class GetConnectionInfoHandler(BaseQueryHandler[GetConnectionInfoQuery, ConnectionInfoDTO]):
    """Обработчик запроса информации о подключении к real-time уведомлениям."""

    SERVER_EVENTS: list[str] = [
        "notification.created",
        "notification.read",
        "notification.all_read",
        "notification.archived",
    ]

    CLIENT_MESSAGES: list[str] = ["ping"]

    HEARTBEAT_INTERVAL_SEC: int = 30

    def __init__(self, *, host: str, port: int, api_prefix: str, debug: bool = False, base_url: str = "") -> None:
        super().__init__()
        if base_url:
            # Derive WS URL from public base_url (e.g. https://backend.julow.ru → wss://backend.julow.ru)
            ws_base = base_url.replace("https://", "wss://").replace("http://", "ws://")
            self._websocket_url = f"{ws_base}{api_prefix}/ws/notifications"
        else:
            scheme = "ws" if debug else "wss"
            self._websocket_url = f"{scheme}://{host}:{port}{api_prefix}/ws/notifications"

    async def handle(self, query: GetConnectionInfoQuery) -> ConnectionInfoDTO:
        return ConnectionInfoDTO(
            websocket_url=self._websocket_url,
            auth_method="query",
            auth_param="token",
            heartbeat_interval_sec=self.HEARTBEAT_INTERVAL_SEC,
            server_events=list(self.SERVER_EVENTS),
            client_messages=list(self.CLIENT_MESSAGES),
        )
