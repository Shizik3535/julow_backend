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
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Принять и зарегистрировать WebSocket-соединение."""
        await websocket.accept()
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
        logger.info("WebSocket connected", user_id=user_id)

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Удалить WebSocket-соединение из реестра."""
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]
        logger.info("WebSocket disconnected", user_id=user_id)

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
