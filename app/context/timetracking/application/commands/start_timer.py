from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
from app.context.timetracking.application.exceptions.timetracking_app_exceptions import (
    TimeEntryEpicNotFoundException,
    TimeEntryProjectNotFoundException,
    TimeEntryTaskNotFoundException,
    TimeEntryWorkspaceNotFoundException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.application.ports.integration.inboard.epic_port import EpicPort
from app.context.timetracking.application.ports.integration.inboard.project_port import ProjectPort
from app.context.timetracking.application.ports.integration.inboard.task_port import TaskPort
from app.context.timetracking.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.timetracking.domain.aggregates.time_entry import TimeEntry
from app.context.timetracking.domain.exceptions.time_entry_exceptions import (
    TimerAlreadyRunningException,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class StartTimerCommand(BaseCommand):
    """
    Команда запуска таймера.

    Если у пользователя нет активной записи (RUNNING/PAUSED) — создаётся новая
    запись со статусом DRAFT и таймер сразу запускается.
    """

    caller_id: str
    workspace_id: str
    task_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str | None = None


class StartTimerHandler(BaseCommandHandler[StartTimerCommand, TimeEntryDTO]):
    """Запуск таймера. Гарантирует только один активный таймер на пользователя."""

    REQUIRED_PERMISSION = "time.write"

    def __init__(
        self,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        workspace_port: WorkspacePort,
        task_port: TaskPort,
        project_port: ProjectPort,
        epic_port: EpicPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = time_entry_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._task_port = task_port
        self._project_port = project_port
        self._epic_port = epic_port
        self._event_bus = event_bus

    async def handle(self, command: StartTimerCommand) -> TimeEntryDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise TimeEntryWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        # Проверка single-active-timer
        existing = await self._repo.get_running_timer(Id.from_string(command.caller_id))
        if existing is not None:
            raise TimerAlreadyRunningException()

        # Валидация связей
        if command.task_id and not await self._task_port.task_exists(command.task_id):
            raise TimeEntryTaskNotFoundException(command.task_id)
        if command.project_id and not await self._project_port.project_exists(command.project_id):
            raise TimeEntryProjectNotFoundException(command.project_id)
        if command.epic_id and not await self._epic_port.epic_exists(command.epic_id):
            raise TimeEntryEpicNotFoundException(command.epic_id)

        # Создаём пустой TimeEntry и стартуем таймер
        from datetime import date as _date

        entry = TimeEntry.create_for_timer(
            user_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            entry_date=_date.today(),
            description=command.description,
        )
        entry.start_timer(
            task_id=Id.from_string(command.task_id) if command.task_id else None,
            project_id=Id.from_string(command.project_id) if command.project_id else None,
            epic_id=Id.from_string(command.epic_id) if command.epic_id else None,
        )
        await self._repo.add(entry)
        await self._event_bus.publish_all(entry.clear_domain_events())
        return time_entry_to_dto(entry)
