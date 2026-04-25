from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository


class DeleteTaskTemplateCommand(BaseCommand):
    """
    Команда удаления шаблона задачи.

    Атрибуты:
        caller_id: ID вызывающего.
        template_id: ID шаблона.
    """

    caller_id: str
    template_id: str


class DeleteTaskTemplateHandler(BaseCommandHandler[DeleteTaskTemplateCommand, None]):
    """Обработчик удаления шаблона задачи."""

    REQUIRED_PERMISSION = "tasks.templates.manage"

    def __init__(
        self,
        template_repo: TaskTemplateRepository,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._template_repo = template_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeleteTaskTemplateCommand) -> None:
        template = await self._template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise TaskTemplateNotFoundException(id=command.template_id)

        if template.project_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                project_id=str(template.project_id),
                permission=self.REQUIRED_PERMISSION,
            )

        template.mark_deleted()
        await self._template_repo.delete(template.id)
        await self._event_bus.publish_all(template.clear_domain_events())
