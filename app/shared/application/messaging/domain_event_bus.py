from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.domain.base_domain_event import BaseDomainEvent


class DomainEventBus(ABC):
    """
    Шина доменных событий Bounded Context'а.

    Use case вызывает ``event_bus.publish_all(events)`` после
    успешного сохранения агрегата. Шина отвечает за сериализацию
    и доставку событий во внешний транспорт (брокер сообщений).

    Каждый BC имеет свой экземпляр, привязанный к собственному
    топику (``identity.events``, ``profile.events`` и т.д.).
    При переходе на микросервисы меняется только реализация —
    API шины и use-case'ов не меняется.

    Пример:
        events = aggregate.clear_domain_events()
        await self._event_bus.publish_all(events)
    """

    @abstractmethod
    async def publish_all(self, events: list[BaseDomainEvent]) -> None:
        """
        Опубликовать список доменных событий в топик BC.

        Аргументы:
            events: События, собранные из агрегата через ``clear_domain_events()``.
        """
