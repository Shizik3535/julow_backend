from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.shared.domain.base_entity import BaseEntity


@dataclass
class AggregateRoot(BaseEntity):
    """
    Базовый корень агрегата (Aggregate Root).

    Aggregate Root — точка входа в агрегат. Все изменения
    объектов внутри агрегата выполняются через корень.
    Корень гарантирует консистентность агрегата.

    Атрибуты:
        _domain_events: Список доменных событий, порождённых агрегатом.

    Правила DDD:
        - Только Aggregate Root может быть загружен напрямую из Repository
        - Внутренние сущности агрегата доступны только через корень
        - Транзакционная граница — один агрегат
        - Доменные события собираются и диспетчируются после сохранения

    Пример:
        class Order(AggregateRoot):
            items: list[OrderItem]
            status: OrderStatus

            def add_item(self, item: OrderItem) -> None:
                self.items.append(item)
                self._register_event(ItemAdded(order_id=self.id, item_id=item.id))
    """

    _domain_events: list[BaseDomainEvent] = field(default_factory=list, init=False, repr=False)

    def _register_event(self, event: BaseDomainEvent) -> None:
        """
        Регистрирует доменное событие.

        Автоматически заполняет aggregate_id и aggregate_type
        на основе текущего агрегата. События будут извлечены
        и отправлены после успешного сохранения агрегата.

        Аргументы:
            event: Доменное событие для регистрации.
        """
        object.__setattr__(event, "aggregate_id", self.id)
        object.__setattr__(event, "aggregate_type", type(self).__name__)
        self._domain_events.append(event)

    def clear_domain_events(self) -> list[BaseDomainEvent]:
        """
        Извлекает и очищает все доменные события.

        Возвращает список событий для последующей диспетчеризации.
        Обычно вызывается Application Layer после сохранения агрегата.

        Возвращает:
            Список доменных событий, порождённых агрегатом.
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> list[BaseDomainEvent]:
        """Возвращает копию списка доменных событий (без очистки)."""
        return list(self._domain_events)
