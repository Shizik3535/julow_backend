from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine


MessageHandler = Callable[[str, dict[str, Any]], Coroutine[Any, Any, None]]


class MessageBrokerPort(ABC):
    """
    Порт (интерфейс) для брокера сообщений.

    Абстрагирует работу с Kafka, RabbitMQ и т.д.
    Используется для коммуникации между Bounded Context'ами
    через доменные события.

    При переходе на микросервисы этот порт заменяет
    in-process диспетчер на реальный брокер.

    Методы:
        publish: Опубликовать сообщение в топик.
        subscribe: Подписаться на топик с обработчиком.
        start: Запустить консьюмер.
        stop: Остановить консьюмер.

    Правила:
        - Сообщения публикуются в топики / очереди
        - Подписчик получает сообщения асинхронно
        - Поддерживается как минимум one-time доставка
    """

    @abstractmethod
    async def publish(self, topic: str, message: dict[str, Any], key: str | None = None) -> None:
        """
        Опубликовать сообщение в топик.

        Аргументы:
            topic: Имя топика.
            message: Сообщение (сериализуемое в JSON).
            key: Ключ сообщения для партиционирования (опционально).
        """

    @abstractmethod
    async def subscribe(self, topic: str, group_id: str, handler: MessageHandler) -> None:
        """
        Подписаться на топик с обработчиком.

        Аргументы:
            topic: Имя топика.
            group_id: Идентификатор группы консьюмеров.
            handler: Асинхронная функция-обработчик сообщения.
        """

    @abstractmethod
    async def start(self) -> None:
        """Запустить консьюмер (начать обработку сообщений)."""

    @abstractmethod
    async def stop(self) -> None:
        """Остановить консьюмер."""
