from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class ActivityCategoryDTO(BaseDTO):
    """
    DTO категории деятельности (TimeTracking BC).

    Атрибуты:
        id: Идентификатор.
        name: Название.
        color: HEX-цвет (#RRGGBB).
        is_system: Системная ли.
        description: Описание.
        is_deleted: Помечена ли удалённой.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: str
    workspace_id: str | None = None
    name: str
    color: str | None = None
    is_system: bool = False
    description: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ActivityCategoryListDTO(BaseDTO):
    """Список категорий с total."""

    items: list[ActivityCategoryDTO]
    total: int
