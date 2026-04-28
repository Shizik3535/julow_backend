from __future__ import annotations

from app.core.logging import get_logger
from app.shared.application.ports.notification.websocket_dto import WebSocketMessage
from app.shared.application.ports.notification.websocket_port import WebSocketPort
from app.shared.infrastructure.notification.websocket_manager import WebSocketManager

logger = get_logger(__name__)


class WebSocketAdapter(WebSocketPort):
    """
    Реализация WebSocketPort на основе WebSocketManager.

    Делегирует отправку сообщений в in-memory менеджер
    WebSocket-соединений.
    """

    def __init__(self, manager: WebSocketManager) -> None:
        self._manager = manager

    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> None:
        data = {
            "event_type": message.event_type,
            "payload": message.payload,
        }
        await self._manager.send_to_user(user_id, data)
        logger.debug("WebSocket message sent to user", user_id=user_id, event_type=message.event_type)

    async def broadcast(self, message: WebSocketMessage) -> None:
        data = {
            "event_type": message.event_type,
            "payload": message.payload,
        }
        await self._manager.broadcast(data)
        logger.debug("WebSocket message broadcast", event_type=message.event_type)
