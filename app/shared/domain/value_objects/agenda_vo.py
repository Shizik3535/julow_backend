from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.agenda_item import AgendaItem


@dataclass(frozen=True)
class Agenda(ValueObject):
    """
    Value Object для повестки совещания.

    Атрибуты:
        items: Список пунктов повестки.
    """

    items: list[AgendaItem] = field(default_factory=list)
