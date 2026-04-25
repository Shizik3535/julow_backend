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
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository


class CreateTaskFromTemplateCommand(BaseCommand):
    """
    Команда создания задачи из шаблона.

    Атрибуты:
        project_id: ID проекта.
        template_id: ID шаблона задачи.
        reporter_id: ID автора.
    """

    caller_id: str
    project_id: str
    template_id: str
    reporter_id: str


class CreateTaskFromTemplateHandler(BaseCommandHandler[CreateTaskFromTemplateCommand, TaskDTO]):
    """Обработчик создания задачи из шаблона."""

    REQUIRED_PERMISSION = "tasks.create"

    def __init__(
        self,
        task_repo: TaskRepository,
        template_repo: TaskTemplateRepository,
        project_port: ProjectPort,
        board_port: BoardPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._template_repo = template_repo
        self._project_port = project_port
        self._board_port = board_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateTaskFromTemplateCommand) -> TaskDTO:
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=command.project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        if not await self._project_port.project_exists(command.project_id):
            raise TaskProjectNotFoundException(command.project_id)
        if not await self._project_port.is_project_active(command.project_id):
            raise TaskProjectArchivedOrSuspendedException(command.project_id)

        template = await self._template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise TaskTemplateNotFoundException(id=command.template_id)

        task = Task.create_from_template(
            template_name=template.name,
            template_type=template.task_type,
            template_labels=template.default_labels,
            template_checklists=template.default_checklists,
            template_custom_fields=template.default_custom_fields,
            project_id=Id.from_string(command.project_id),
            reporter_id=Id.from_string(command.reporter_id),
        )

        default_status_id = await self._board_port.get_default_status_id(command.project_id)
        if default_status_id:
            task.change_status(Id.from_string(default_status_id))

        await self._task_repo.add(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        return TaskDTO(
            id=str(task.id),
            project_id=str(task.project_id),
            title=task.title,
            status_id=str(task.status_id) if task.status_id else None,
            priority=task.priority.value,
            task_type=task.task_type.value,
            reporter_id=str(task.reporter_id) if task.reporter_id else None,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
