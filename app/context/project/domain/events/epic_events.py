from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.project.domain.value_objects.epic_status import EpicStatus


@dataclass(frozen=True)
class EpicCreated(BaseDomainEvent):
    """Эпик создан."""

    project_id: str = ""
    epic_id: str = ""


@dataclass(frozen=True)
class EpicUpdated(BaseDomainEvent):
    """Эпик обновлён."""

    project_id: str = ""
    epic_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EpicStatusChanged(BaseDomainEvent):
    """Статус эпика изменён."""

    project_id: str = ""
    epic_id: str = ""
    new_status: EpicStatus = EpicStatus.OPEN
