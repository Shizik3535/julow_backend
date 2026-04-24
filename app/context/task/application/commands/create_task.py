from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskDTO
from app.context.task.application.exceptions.task_app_exceptions import (
    TaskProjectNotFoundException,
    TaskProjectArchivedOrSuspendedException,
)
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.project_port import ProjectPort
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.task_type import TaskType


class CreateTaskCommand(BaseCommand):
    """
    Команда создания задачи.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        title: Заголовок.
        task_type: Тип задачи.
        reporter_id: ID автора.
        parent_task_id: ID родительской задачи.
        epic_id: ID эпика.
    """

    caller_id: str
    project_id: str
    title: str
    task_type: str = "TASK"
    reporter_id: str = ""
    parent_task_id: str | None = None
    epic_id: str | None = None


class CreateTaskHandler(BaseCommandHandler[CreateTaskCommand, TaskDTO]):
    """
    Обработчик создания задачи.

    Проверяет существование и активность проекта,
    назначает default workflow status.
    """

    REQUIRED_PERMISSION = "tasks.create"

    def __init__(
        self,
        task_repo: TaskRepository,
        project_port: ProjectPort,
        board_port: BoardPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._project_port = project_port
        self._board_port = board_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateTaskCommand) -> TaskDTO:
        if not await self._project_port.project_exists(command.project_id):
            raise TaskProjectNotFoundException(command.project_id)
        if not await self._project_port.is_project_active(command.project_id):
            raise TaskProjectArchivedOrSuspendedException(command.project_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=command.project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        parent_id = Id.from_string(command.parent_task_id) if command.parent_task_id else None
        epic_id = Id.from_string(command.epic_id) if command.epic_id else None

        task = Task.create(
            title=command.title,
            project_id=Id.from_string(command.project_id),
            task_type=TaskType(command.task_type),
            reporter_id=Id.from_string(command.reporter_id),
            parent_task_id=parent_id,
            epic_id=epic_id,
        )

        default_status_id = await self._board_port.get_default_status_id(command.project_id)
        if default_status_id:
            task.change_status(Id.from_string(default_status_id))

        await self._task_repo.add(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        return TaskDTO(
            id=str(task.id),
            project_id=str(task.project_id),
            parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
            epic_id=str(task.epic_id) if task.epic_id else None,
            title=task.title,
            status_id=str(task.status_id) if task.status_id else None,
            priority=task.priority.value,
            task_type=task.task_type.value,
            reporter_id=str(task.reporter_id) if task.reporter_id else None,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
