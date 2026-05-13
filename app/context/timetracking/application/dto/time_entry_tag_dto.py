from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class TimeEntryTagDTO(BaseDTO):
    """
    DTO тега записи времени (TimeTracking BC).

    Атрибуты:
        id: Идентификатор.
        workspace_id: ID workspace.
        name: Название.
        color: HEX-цвет (#RRGGBB).
        is_deleted: Помечен ли удалённым.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: str
    workspace_id: str
    name: str
    color: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TimeEntryTagListDTO(BaseDTO):
    """Список тегов с total."""

    items: list[TimeEntryTagDTO]
    total: int
