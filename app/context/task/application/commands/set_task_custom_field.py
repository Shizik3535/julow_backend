from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.integration.inboard.project_port import ProjectPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class SetTaskCustomFieldCommand(BaseCommand):
    """
    Команда установки кастомного поля задачи.

    Атрибуты:
        task_id: ID задачи.
        field_name: Имя поля.
        value: Значение.
        changed_by: ID изменившего.
    """

    task_id: str
    field_name: str
    value: str
    changed_by: str


class SetTaskCustomFieldHandler(BaseCommandHandler[SetTaskCustomFieldCommand, None]):
    """
    Обработчик установки кастомного поля.

    Валидация имени поля через ProjectPort (CustomFieldDefinition).
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        project_port: ProjectPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._project_port = project_port
        self._event_bus = event_bus

    async def handle(self, command: SetTaskCustomFieldCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        old_value = task.custom_fields.get(command.field_name)
        task.set_custom_field(command.field_name, command.value)
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name=f"custom_field:{command.field_name}",
            old_value=old_value,
            new_value=command.value,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)
