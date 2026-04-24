from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.task.application.dto.task_template_dto import TaskTemplateDTO
from app.context.task.application.exceptions.task_template_app_exceptions import TaskTemplateAlreadyExistsException
from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository
from app.context.task.domain.value_objects.task_type import TaskType


class CreateTaskTemplateCommand(BaseCommand):
    """
    Команда создания кастомного шаблона задачи.

    Атрибуты:
        name: Название шаблона.
        task_type: Тип задачи.
    """

    name: str
    task_type: str = "TASK"


class CreateTaskTemplateHandler(BaseCommandHandler[CreateTaskTemplateCommand, TaskTemplateDTO]):
    """Обработчик создания кастомного шаблона задачи."""

    def __init__(
        self,
        template_repo: TaskTemplateRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._template_repo = template_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateTaskTemplateCommand) -> TaskTemplateDTO:
        existing = await self._template_repo.get_by_name(command.name)
        if existing is not None:
            raise TaskTemplateAlreadyExistsException(command.name)

        template = TaskTemplate.create_custom(
            name=command.name,
            task_type=TaskType(command.task_type),
        )
        await self._template_repo.add(template)
        await self._event_bus.publish_all(template.clear_domain_events())

        return TaskTemplateDTO(
            id=str(template.id),
            name=template.name,
            task_type=template.task_type.value,
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
