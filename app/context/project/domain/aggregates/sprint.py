from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.entities.sprint_retro import SprintRetro
from app.context.project.domain.events.sprint_events import (
    SprintCreated,
    SprintStarted,
    SprintCompleted,
    SprintCancelled,
    SprintGoalUpdated,
    SprintRetroCreated,
    TasksMovedToNextSprint,
    TasksMovedToBacklog,
)
from app.context.project.domain.exceptions.sprint_exceptions import (
    SprintAlreadyStartedException,
    SprintNotStartedException,
)


@dataclass
class Sprint(AggregateRoot):
    """
    Корень агрегата спринта (Project BC).

    Атрибуты:
        project_id: Opaque ID проекта.
        name: Название спринта.
        goal: Цель спринта.
        status: Статус спринта.
        date_range: Диапазон дат (из shared kernel).
        retro: Ретроспектива (entity).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id = field(default_factory=Id.generate)
    name: str = ""
    goal: SprintGoal | None = None
    status: SprintStatus = SprintStatus.PLANNING
    date_range: DateRange | None = None
    retro: SprintRetro | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, name: str, project_id: Id, goal: SprintGoal | None = None, date_range: DateRange | None = None) -> Sprint:
        """Создаёт спринт."""
        sprint = cls(name=name, project_id=project_id, goal=goal, date_range=date_range)
        sprint._register_event(
            SprintCreated(sprint_id=str(sprint.id), project_id=str(project_id), name=name)
        )
        return sprint

    def start(self) -> None:
        """Запускает спринт."""
        if self.status != SprintStatus.PLANNING:
            raise SprintAlreadyStartedException()
        self.status = SprintStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SprintStarted(sprint_id=str(self.id)))

    def complete(self, incomplete_task_ids: list[Id] | None = None, next_sprint_id: Id | None = None) -> None:
        """Завершает спринт. Незавершённые задачи перемещаются на app-слое."""
        if self.status != SprintStatus.ACTIVE:
            raise SprintNotStartedException()
        self.status = SprintStatus.COMPLETED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SprintCompleted(sprint_id=str(self.id)))
        if incomplete_task_ids:
            task_ids = [str(tid) for tid in incomplete_task_ids]
            if next_sprint_id is not None:
                self._register_event(
                    TasksMovedToNextSprint(sprint_id=str(self.id), task_ids=task_ids)
                )
            else:
                self._register_event(
                    TasksMovedToBacklog(sprint_id=str(self.id), task_ids=task_ids)
                )

    def cancel(self) -> None:
        """Отменяет спринт."""
        if self.status not in (SprintStatus.PLANNING, SprintStatus.ACTIVE):
            return
        self.status = SprintStatus.CANCELLED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SprintCancelled(sprint_id=str(self.id)))

    def update_goal(self, goal: SprintGoal) -> None:
        """Обновляет цель спринта."""
        self.goal = goal
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SprintGoalUpdated(sprint_id=str(self.id)))

    def update_date_range(self, date_range: DateRange | None) -> None:
        """Обновляет диапазон дат спринта."""
        self.date_range = date_range
        self.updated_at = datetime.now(tz=timezone.utc)

    def create_retro(self, template_name: str, sections: list[RetroSection]) -> None:
        """Создаёт ретроспективу для спринта."""
        self.retro = SprintRetro(template_name=template_name, sections=sections)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SprintRetroCreated(sprint_id=str(self.id), template_name=template_name)
        )
