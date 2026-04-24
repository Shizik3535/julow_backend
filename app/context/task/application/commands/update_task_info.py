from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class UpdateTaskInfoCommand(BaseCommand):
    """
    Команда обновления информации задачи.

    Атрибуты:
        task_id: ID задачи.
        changed_by: ID изменившего.
        title: Новый заголовок.
        description_content: Контент описания.
        description_format: Формат описания.
        start_date: Дата начала (ISO).
        due_date: Дедлайн (ISO).
    """

    task_id: str
    changed_by: str
    title: str | None = None
    description_content: str | None = None
    description_format: str | None = None
    start_date: str | None = None
    due_date: str | None = None


class UpdateTaskInfoHandler(BaseCommandHandler[UpdateTaskInfoCommand, None]):
    """Обработчик обновления информации задачи с записью в changelog."""

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateTaskInfoCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.changed_by,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        old_title = task.title
        old_start = str(task.start_date) if task.start_date else None
        old_due = str(task.due_date) if task.due_date else None

        description: RichText | None = None
        if command.description_content is not None:
            from app.shared.domain.value_objects.rich_text_format import RichTextFormat
            fmt = RichTextFormat(command.description_format) if command.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=command.description_content, format=fmt)

        start_date = date.fromisoformat(command.start_date) if command.start_date else None
        due_date = date.fromisoformat(command.due_date) if command.due_date else None

        task.update_info(
            title=command.title,
            description=description,
            start_date=start_date,
            due_date=due_date,
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        changed_by = Id.from_string(command.changed_by)
        task_id = Id.from_string(command.task_id)
        if command.title and command.title != old_title:
            entry = ChangelogEntry.create(task_id=task_id, field_name="title", old_value=old_title, new_value=command.title, changed_by=changed_by)
            await self._changelog_repo.add(entry)
        if command.start_date and command.start_date != old_start:
            entry = ChangelogEntry.create(task_id=task_id, field_name="start_date", old_value=old_start, new_value=command.start_date, changed_by=changed_by)
            await self._changelog_repo.add(entry)
        if command.due_date and command.due_date != old_due:
            entry = ChangelogEntry.create(task_id=task_id, field_name="due_date", old_value=old_due, new_value=command.due_date, changed_by=changed_by)
            await self._changelog_repo.add(entry)
