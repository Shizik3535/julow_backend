from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.shared.application.ports.notification.push_dto import PushMessage


class PushPort(ABC):
    """
    Порт (интерфейс) для отправки push-уведомлений.

    Абстрагирует работу с Firebase Cloud Messaging, OneSignal и т.д.
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        send: Отправить push конкретному пользователю.
        send_to_topic: Отправить push на тему (группе устройств).
        send_batch: Отправить несколько push-уведомлений пакетом.

    Правила:
        - Push отправляется асинхронно
        - Ошибки отправки логируются, но не ломают основной поток
        - Получатель идентифицируется по user_id (не device token)
    """

    @abstractmethod
    async def send(self, message: PushMessage) -> None:
        """
        Отправить push-уведомление пользователю.

        Аргументы:
            message: Push-уведомление для отправки.
        """

    @abstractmethod
    async def send_to_topic(self, topic: str, title: str, body: str, data: dict[str, Any] | None = None) -> None:
        """
        Отправить push-уведомление на тему (группе устройств).

        Аргументы:
            topic: Имя темы (например, "project_123").
            title: Заголовок уведомления.
            body: Текст уведомления.
            data: Дополнительные данные (опционально).
        """

    @abstractmethod
    async def send_batch(self, messages: tuple[PushMessage, ...]) -> None:
        """
        Отправить несколько push-уведомлений пакетом.

        Аргументы:
            messages: Кортеж push-уведомлений для отправки.
        """
