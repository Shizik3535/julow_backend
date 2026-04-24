from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class ChangelogEntryDTO(BaseDTO):
    """
    DTO записи истории изменений (Task BC).

    Атрибуты:
        id: Идентификатор записи.
        task_id: ID задачи.
        field_name: Имя поля.
        old_value: Старое значение.
        new_value: Новое значение.
        changed_by: ID изменившего.
        changed_at: Время изменения.
    """

    id: str
    task_id: str
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by: str = ""
    changed_at: datetime | None = None


class ChangelogListDTO(BaseDTO):
    """Список записей changelog с total."""

    items: list[ChangelogEntryDTO]
    total: int
