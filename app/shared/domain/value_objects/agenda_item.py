from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.id_vo import Id


@dataclass(frozen=True)
class AgendaItem(ValueObject):
    """
    Value Object для пункта повестки.

    Атрибуты:
        text: Текст пункта.
        duration_minutes: Длительность в минутах (None — без ограничения).
        owner_id: ID ответственного (None — не назначен).
    """

    text: str = ""
    duration_minutes: int | None = None
    owner_id: Id | None = None
