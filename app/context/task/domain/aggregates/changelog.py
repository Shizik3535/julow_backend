from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.events.changelog_events import ChangelogEntryCreated


@dataclass
class ChangelogEntry(AggregateRoot):
    """
    Корень агрегата записи истории изменений (Task BC).

    Отдельный AR — не загружается в Task. Доступ через ChangelogRepository
    с пагинацией. Тысячи записей не загружаются в память.

    Атрибуты:
        task_id: Opaque ID задачи.
        field_name: Имя изменённого поля.
        old_value: Старое значение.
        new_value: Новое значение.
        changed_by: ID изменившего.
        changed_at: Время изменения.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    task_id: Id = field(default_factory=Id.generate)
    field_name: str = ""
    old_value: str | None = None
    new_value: str | None = None
    changed_by: Id = field(default_factory=Id.generate)
    changed_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        task_id: Id,
        field_name: str,
        old_value: str | None,
        new_value: str | None,
        changed_by: Id,
    ) -> ChangelogEntry:
        """Создаёт запись истории изменений."""
        entry = cls(
            task_id=task_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
        )
        entry._register_event(
            ChangelogEntryCreated(task_id=str(task_id), field_name=field_name)
        )
        return entry
