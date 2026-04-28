from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

from app.shared.application.ports.notification.websocket_dto import WebSocketMessage


class WebSocketPort(ABC):
    """
    Порт (интерфейс) для отправки сообщений через WebSocket.

    Абстрагирует работу с WebSocket-соединениями.
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        send_to_user: Отправить сообщение конкретному пользователю.
        broadcast: Отправить сообщение всем подключённым пользователям.

    Правила:
        - Сообщения отправляются асинхронно
        - Если пользователь не подключён — сообщение игнорируется
        - Ошибки отправки логируются, но не ломают основной поток
    """

    @abstractmethod
    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> None:
        """
        Отправить сообщение конкретному пользователю.

        Аргументы:
            user_id: ID пользователя-получателя.
            message: Сообщение для отправки.
        """

    @abstractmethod
    async def broadcast(self, message: WebSocketMessage) -> None:
        """
        Отправить сообщение всем подключённым пользователям.

        Аргументы:
            message: Сообщение для отправки.
        """
