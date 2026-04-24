from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color


@dataclass
class TimeEntryTag(AggregateRoot):
    """
    Корень агрегата тега записи времени (TimeTracking BC).

    Атрибуты:
        name: Название тега.
        color: Цвет (из shared kernel).
        is_deleted: Удалён ли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    color: Color | None = None
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, name: str, color: Color | None = None) -> TimeEntryTag:
        """Создаёт тег."""
        return cls(name=name, color=color)

    def update(self, name: str | None = None, color: Color | None = None) -> None:
        """Обновляет тег."""
        if name is not None:
            self.name = name
        if color is not None:
            self.color = color
        self.updated_at = datetime.now(tz=timezone.utc)

    def delete(self) -> None:
        """Помечает тег как удалённый."""
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
