from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class SprintCreated(BaseDomainEvent):
    """Спринт создан."""

    sprint_id: str = ""
    project_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class SprintStarted(BaseDomainEvent):
    """Спринт запущен."""

    sprint_id: str = ""


@dataclass(frozen=True)
class SprintCompleted(BaseDomainEvent):
    """Спринт завершён."""

    sprint_id: str = ""


@dataclass(frozen=True)
class SprintCancelled(BaseDomainEvent):
    """Спринт отменён."""

    sprint_id: str = ""


@dataclass(frozen=True)
class SprintGoalUpdated(BaseDomainEvent):
    """Цель спринта обновлена."""

    sprint_id: str = ""


@dataclass(frozen=True)
class SprintRetroCreated(BaseDomainEvent):
    """Ретроспектива создана."""

    sprint_id: str = ""
    template_name: str = ""


@dataclass(frozen=True)
class TasksMovedToNextSprint(BaseDomainEvent):
    """Незавершённые задачи перемещены в следующий спринт."""

    sprint_id: str = ""
    task_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TasksMovedToBacklog(BaseDomainEvent):
    """Незавершённые задачи перемещены в бэклог."""

    sprint_id: str = ""
    task_ids: list[str] = field(default_factory=list)
