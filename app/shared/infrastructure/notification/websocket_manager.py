from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """
    Менеджер WebSocket-соединений.

    Хранит in-memory отображение user_id → set[WebSocket].
    Поддерживает подключение/отключение, отправку
    конкретному пользователю и широковещательную рассылку.

    Правила:
        - Один пользователь может иметь несколько соединений (несколько вкладок)
        - Отключённые соединения удаляются автоматически
        - Потокобезопасность через asyncio.Lock
    """

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        # Какие чаты пользователь сейчас активно смотрит на каждом сокете.
        # Ключ — конкретный WebSocket (а не user_id), потому что у одного
        # юзера могут быть открыты разные чаты в разных вкладках; нам важно
        # знать «есть ли ХОТЯ БЫ ОДНА» вкладка пользователя на чате X.
        self._socket_chats: dict[WebSocket, set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Принять и зарегистрировать WebSocket-соединение."""
        await websocket.accept()
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
            self._socket_chats.setdefault(websocket, set())
        logger.info("WebSocket connected", user_id=user_id)

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Удалить WebSocket-соединение из реестра."""
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]
            self._socket_chats.pop(websocket, None)
        logger.info("WebSocket disconnected", user_id=user_id)

    async def subscribe_chat(self, websocket: WebSocket, chat_id: str) -> None:
        """Отметить, что данный сокет сейчас активно смотрит этот чат.

        Используется фронтом, когда пользователь открывает чат на странице
        ``/chats``. Пока сокет «смотрит» чат, мы не создаём для него
        notifications о новых сообщениях в этом чате (см.
        ``OnMessageSentNotify``) — он и так видит их в ленте через realtime.
        """
        if not chat_id:
            return
        async with self._lock:
            self._socket_chats.setdefault(websocket, set()).add(chat_id)

    async def unsubscribe_chat(self, websocket: WebSocket, chat_id: str) -> None:
        """Снять отметку «сокет смотрит этот чат» (закрыли тред / ушли с страницы)."""
        if not chat_id:
            return
        async with self._lock:
            chats = self._socket_chats.get(websocket)
            if chats is not None:
                chats.discard(chat_id)

    def is_user_viewing_chat(self, user_id: str, chat_id: str) -> bool:
        """Смотрит ли пользователь данный чат хотя бы в одной вкладке?

        Без блокировки — это горячий путь и допустимы редкие гонки
        (на которые мы и так fallback'имся через сам факт persisted
        notification'а в БД).
        """
        sockets = self._connections.get(user_id)
        if not sockets:
            return False
        for ws in sockets:
            chats = self._socket_chats.get(ws)
            if chats and chat_id in chats:
                return True
        return False

    async def send_to_user(self, user_id: str, data: dict[str, Any]) -> None:
        """Отправить JSON-сообщение всем соединениям пользователя."""
        async with self._lock:
            sockets = list(self._connections.get(user_id, set()))

        for ws in sockets:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning("WebSocket send failed", user_id=user_id, error=str(e))
                await self.disconnect(user_id, ws)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Отправить JSON-сообщение всем подключённым пользователям."""
        async with self._lock:
            all_sockets = [
                ws
                for sockets in self._connections.values()
                for ws in sockets
            ]

        for ws in all_sockets:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning("WebSocket broadcast send failed", error=str(e))

    def is_connected(self, user_id: str) -> bool:
        """Проверить, есть ли активные соединения у пользователя.

        Note: Читает _connections без блокировки для синхронного API.
        Может вернуть устаревшие данные в конкурентной среде.
        """
        return user_id in self._connections and len(self._connections[user_id]) > 0
