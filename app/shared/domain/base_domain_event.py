from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.value_objects.id_vo import Id


@dataclass(frozen=True)
class BaseDomainEvent:
    """
    Базовое доменное событие.

    Доменное событие фиксирует факт того, что произошло
    что-то значимое в домене. События используются для:
    - Коммуникации между Bounded Context'ами
    - Побочных эффектов (отправка уведомлений, синхронизация)
    - Аудита и отслеживания изменений

    Атрибуты:
        event_id: Уникальный идентификатор события.
        aggregate_id: ID агрегата, породившего событие.
        aggregate_type: Имя типа агрегата.
        occurred_at: Время возникновения события (UTC).
        event_type: Имя типа события (автоматически).

    Правила DDD:
        - Событие неизменяемо (frozen dataclass)
        - Событие именуется в прошедшем времени (TaskCreated, UserRegistered)
        - Событие содержит всё необходимое для обработки
    """

    event_id: Id = field(default_factory=Id.generate)
    aggregate_id: Id = field(default_factory=Id.generate)
    aggregate_type: str = ""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    event_type: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", type(self).__name__)
