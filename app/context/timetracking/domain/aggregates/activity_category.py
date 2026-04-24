from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.timetracking.domain.events.category_events import (
    ActivityCategoryCreated,
    ActivityCategoryDeleted,
)
from app.context.timetracking.domain.exceptions.category_exceptions import (
    CannotDeleteSystemCategoryException,
)


@dataclass
class ActivityCategory(AggregateRoot):
    """
    Корень агрегата категории деятельности (TimeTracking BC).

    Системные категории (is_system=True) нельзя удалить.
    Новые категории = запись с is_system=False.

    Атрибуты:
        name: Название категории.
        color: Цвет (из shared kernel).
        is_system: Системная ли категория.
        description: Описание.
        is_deleted: Удалена ли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    color: Color | None = None
    is_system: bool = False
    description: str | None = None
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create_system(cls, name: str, description: str | None = None) -> ActivityCategory:
        """Создаёт системную категорию."""
        category = cls(name=name, is_system=True, description=description)
        category._register_event(
            ActivityCategoryCreated(category_id=str(category.id), name=name)
        )
        return category

    @classmethod
    def create_custom(cls, name: str, color: Color | None = None, description: str | None = None) -> ActivityCategory:
        """Создаёт пользовательскую категорию."""
        category = cls(name=name, color=color, is_system=False, description=description)
        category._register_event(
            ActivityCategoryCreated(category_id=str(category.id), name=name)
        )
        return category

    def update(self, name: str | None = None, color: Color | None = None, description: str | None = None) -> None:
        """Обновляет категорию (системную можно обновить частично)."""
        if name is not None:
            self.name = name
        if color is not None:
            self.color = color
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)

    def assert_deletable(self) -> None:
        """Проверяет, что категорию можно удалить."""
        if self.is_system:
            raise CannotDeleteSystemCategoryException(name=self.name)

    def mark_deleted(self) -> None:
        """Помечает категорию как удалённую."""
        self.assert_deletable()
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ActivityCategoryDeleted(category_id=str(self.id)))
