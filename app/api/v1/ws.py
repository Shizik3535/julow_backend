from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.logging import get_logger
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.infrastructure.notification.websocket_manager import WebSocketManager

logger = get_logger(__name__)

ws_router = APIRouter()

# WebSocketManager и AuthTokenPort будут установлены из DI при startup
_manager: WebSocketManager | None = None
_auth_token_port: AuthTokenPort | None = None


def set_websocket_manager(manager: WebSocketManager) -> None:
    """Установить WebSocketManager (вызывается при startup из DI)."""
    global _manager
    _manager = manager


def set_auth_token_port(auth_token_port: AuthTokenPort) -> None:
    """Установить AuthTokenPort (вызывается при startup из DI)."""
    global _auth_token_port
    _auth_token_port = auth_token_port


def get_websocket_manager() -> WebSocketManager:
    """Получить WebSocketManager."""
    if _manager is None:
        raise RuntimeError("WebSocketManager not initialized")
    return _manager


@ws_router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    WebSocket endpoint для уведомлений.

    Клиент подключается с JWT-токеном в query-параметре:
        ws://host/ws/notifications?token=<jwt>

    Протокол:
        - Сервер отправляет JSON: {"event_type": "...", "payload": {...}}
        - Клиент отправляет "ping" для heartbeat
        - Сервер отвечает "pong"
    """
    # Валидация JWT и извлечение user_id
    user_id = _extract_user_id_from_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    manager = get_websocket_manager()
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Heartbeat — простой текстовый протокол, не JSON.
            if data == "ping":
                await websocket.send_text("pong")
                continue

            # Любое другое сообщение от клиента трактуем как JSON-команду.
            # На сегодня поддерживаем подписку/отписку на чат: пока сокет
            # «смотрит» чат, бэкенд не создаёт persisted notification про
            # новые сообщения в этом чате (пользователь и так видит их в
            # ленте через realtime).
            try:
                msg = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(msg, dict):
                continue
            action = msg.get("action")
            chat_id = msg.get("chat_id")
            if not isinstance(action, str) or not isinstance(chat_id, str):
                continue
            if action == "chat.subscribe":
                await manager.subscribe_chat(websocket, chat_id)
            elif action == "chat.unsubscribe":
                await manager.unsubscribe_chat(websocket, chat_id)
            # неизвестные действия молча игнорируем — это упрощает
            # эволюцию протокола без поломки старых клиентов
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        await manager.disconnect(user_id, websocket)


def _extract_user_id_from_token(token: str) -> str | None:
    """
    Извлечь user_id из JWT-токена через AuthTokenPort.

    Возвращает:
        user_id (str) при успешной валидации, None при ошибке.
    """
    if _auth_token_port is None:
        logger.warning("AuthTokenPort not initialized, rejecting WebSocket connection")
        return None

    try:
        payload = _auth_token_port.validate_access_token(token)
        return str(payload.user_id)
    except InvalidTokenException:
        logger.debug("WebSocket auth failed: invalid token")
        return None
    except Exception as e:
        logger.error("WebSocket auth error", error=str(e))
        return None
