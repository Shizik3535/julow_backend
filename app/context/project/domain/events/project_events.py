from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.project_visibility import ProjectVisibility
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus


@dataclass(frozen=True)
class ProjectCreated(BaseDomainEvent):
    """Проект создан."""

    project_id: str = ""
    workspace_id: str = ""
    name: str = ""
    methodology: Methodology = Methodology.KANBAN


@dataclass(frozen=True)
class ProjectInfoChanged(BaseDomainEvent):
    """Информация проекта обновлена."""

    project_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectArchived(BaseDomainEvent):
    """Проект архивирован."""

    project_id: str = ""


@dataclass(frozen=True)
class ProjectRestored(BaseDomainEvent):
    """Проект восстановлен."""

    project_id: str = ""


@dataclass(frozen=True)
class ProjectSuspended(BaseDomainEvent):
    """Проект приостановлен."""

    project_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class ProjectReactivated(BaseDomainEvent):
    """Проект реактивирован."""

    project_id: str = ""


@dataclass(frozen=True)
class ProjectDeletionRequested(BaseDomainEvent):
    """Запрос удаления проекта."""

    project_id: str = ""


@dataclass(frozen=True)
class MethodologyChanged(BaseDomainEvent):
    """Методология изменена."""

    project_id: str = ""
    old_methodology: Methodology = Methodology.KANBAN
    new_methodology: Methodology = Methodology.KANBAN


@dataclass(frozen=True)
class ProjectVisibilityChanged(BaseDomainEvent):
    """Видимость проекта изменена."""

    project_id: str = ""
    new_visibility: ProjectVisibility = ProjectVisibility.PRIVATE


@dataclass(frozen=True)
class MilestoneCreated(BaseDomainEvent):
    """Milestone создан."""

    project_id: str = ""
    milestone_id: str = ""


@dataclass(frozen=True)
class MilestoneUpdated(BaseDomainEvent):
    """Milestone обновлён."""

    project_id: str = ""
    milestone_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MilestoneStatusChanged(BaseDomainEvent):
    """Статус milestone изменён."""

    project_id: str = ""
    milestone_id: str = ""
    new_status: MilestoneStatus = MilestoneStatus.NOT_STARTED
