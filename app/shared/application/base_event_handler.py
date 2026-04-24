from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from app.shared.application.base_use_case import BaseUseCase
from app.shared.domain.base_domain_event import BaseDomainEvent

TEvent = TypeVar("TEvent", bound=BaseDomainEvent)


class BaseEventHandler(BaseUseCase[TEvent, None], Generic[TEvent]):
    """
    Базовый обработчик доменного события (Event Handler).

    Реагирует на доменные события и выполняет побочные эффекты:
    отправка уведомлений, синхронизация с другими BC, аудит и т.д.

    Параметры типа:
        TEvent: Тип обрабатываемого события.

    Связь с BaseUseCase:
        - Наследует execute() и логгер от BaseUseCase
        - execute() делегирует вызов в handle()
        - Конкретный обработчик реализует только handle()

    Правила:
        - Один EventHandler = одно событие
        - Не должен содержать бизнес-логику
        - Побочные эффекты: уведомления, логирование, интеграция
        - Может порождать новые команды (saga pattern)

    Пример:
        class SendTaskCreatedNotificationHandler(BaseEventHandler[TaskCreated]):
            def __init__(self, notification_port: NotificationPort) -> None:
                super().__init__()
                self.notification_port = notification_port

            async def handle(self, event: TaskCreated) -> None:
                await self.notification_port.send(
                    recipient_id=event.assignee_id,
                    message=f"Вам назначена задача: {event.title}",
                )
    """

    async def execute(self, event: TEvent) -> None:
        """
        Точка входа для обработки события.

        Делегирует выполнение в handle().

        Аргументы:
            event: Доменное событие для обработки.
        """
        return await self.handle(event)

    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        """
        Обработать доменное событие.

        Аргументы:
            event: Доменное событие для обработки.
        """
