from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.value_objects.epic_status import EpicStatus
from app.context.project.domain.events.epic_events import (
    EpicCreated,
    EpicUpdated,
    EpicStatusChanged,
)


@dataclass
class Epic(AggregateRoot):
    """
    Корень агрегата эпика (Project BC).

    Атрибуты:
        project_id: Opaque ID проекта.
        name: Название эпика.
        description: Описание (форматированный текст).
        status: Статус эпика.
        start_date: Дата начала.
        due_date: Дедлайн.
        owner_id: ID владельца.
        color: Цвет эпика (из shared kernel).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id = field(default_factory=Id.generate)
    name: str = ""
    description: RichText | None = None
    status: EpicStatus = EpicStatus.OPEN
    start_date: date | None = None
    due_date: date | None = None
    owner_id: Id | None = None
    color: Color | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, project_id: Id, name: str, owner_id: Id | None = None) -> Epic:
        """Создаёт эпик."""
        epic = cls(project_id=project_id, name=name, owner_id=owner_id)
        epic._register_event(
            EpicCreated(project_id=str(project_id), epic_id=str(epic.id))
        )
        return epic

    def update(
        self,
        name: str | None = None,
        description: RichText | None = None,
        owner_id: Id | None = None,
        color: Color | None = None,
        start_date: date | None = None,
        due_date: date | None = None,
    ) -> None:
        """Обновляет эпик."""
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if owner_id is not None and self.owner_id != owner_id:
            self.owner_id = owner_id
            changed.append("owner_id")
        if color is not None and self.color != color:
            self.color = color
            changed.append("color")
        if start_date is not None and self.start_date != start_date:
            self.start_date = start_date
            changed.append("start_date")
        if due_date is not None and self.due_date != due_date:
            self.due_date = due_date
            changed.append("due_date")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                EpicUpdated(project_id=str(self.project_id), epic_id=str(self.id), changed_fields=changed)
            )

    def change_status(self, new_status: EpicStatus) -> None:
        """Изменяет статус эпика."""
        self.status = new_status
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            EpicStatusChanged(project_id=str(self.project_id), epic_id=str(self.id), new_status=new_status)
        )
