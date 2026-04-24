from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository


class DeleteTaskTemplateCommand(BaseCommand):
    """
    Команда удаления шаблона задачи.

    Атрибуты:
        template_id: ID шаблона.
    """

    template_id: str


class DeleteTaskTemplateHandler(BaseCommandHandler[DeleteTaskTemplateCommand, None]):
    """Обработчик удаления шаблона задачи."""

    def __init__(
        self,
        template_repo: TaskTemplateRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._template_repo = template_repo
        self._event_bus = event_bus

    async def handle(self, command: DeleteTaskTemplateCommand) -> None:
        template = await self._template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise TaskTemplateNotFoundException(id=command.template_id)

        template.mark_deleted()
        await self._template_repo.update(template)
        await self._event_bus.publish_all(template.clear_domain_events())
