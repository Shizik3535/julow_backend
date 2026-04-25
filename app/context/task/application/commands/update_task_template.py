from __future__ import annotations

from typing import Any

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.entities.checklist import Checklist
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository
from app.context.task.domain.value_objects.label import Label


class UpdateTaskTemplateCommand(BaseCommand):
    """
    Команда обновления шаблона задачи.

    Атрибуты:
        caller_id: ID вызывающего.
        template_id: ID шаблона.
        default_labels: Метки по умолчанию.
        default_checklists: Чек-листы по умолчанию.
        default_custom_fields: Кастомные поля по умолчанию.
    """

    caller_id: str
    template_id: str
    default_labels: list[dict[str, Any]] | None = None
    default_checklists: list[dict[str, Any]] | None = None
    default_custom_fields: dict[str, str] | None = None


class UpdateTaskTemplateHandler(BaseCommandHandler[UpdateTaskTemplateCommand, None]):
    """Обработчик обновления шаблона задачи."""

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

    async def handle(self, command: UpdateTaskTemplateCommand) -> None:
        template = await self._template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise TaskTemplateNotFoundException(id=command.template_id)

        if template.project_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                project_id=str(template.project_id),
                permission=self.REQUIRED_PERMISSION,
            )

        labels: list[Label] | None = None
        if command.default_labels is not None:
            labels = [
                Label(
                    name=lb["name"],
                    color=Color(value=lb["color"]) if lb.get("color") else None,
                )
                for lb in command.default_labels
            ]

        checklists: list[Checklist] | None = None
        if command.default_checklists is not None:
            checklists = [Checklist(title=cl["title"]) for cl in command.default_checklists]

        template.update(
            default_labels=labels,
            default_checklists=checklists,
            default_custom_fields=command.default_custom_fields,
        )
        await self._template_repo.update(template)
        await self._event_bus.publish_all(template.clear_domain_events())
