from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class AddChecklistItemCommand(BaseCommand):
    """
    Команда добавления пункта чек-листа.

    Атрибуты:
        task_id: ID задачи.
        checklist_id: ID чек-листа.
        text: Текст пункта.
        assignee_id: ID исполнителя пункта.
        due_date: Срок выполнения (ISO).
    """

    caller_id: str
    task_id: str
    checklist_id: str
    text: str
    assignee_id: str | None = None
    due_date: str | None = None


class AddChecklistItemHandler(BaseCommandHandler[AddChecklistItemCommand, None]):
    """Обработчик добавления пункта чек-листа."""

    REQUIRED_PERMISSION = "tasks.update_own"

    def __init__(self, task_repo: TaskRepository, permission_checker: TaskPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddChecklistItemCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        assignee_id = Id.from_string(command.assignee_id) if command.assignee_id else None
        item_due_date = date.fromisoformat(command.due_date) if command.due_date else None

        task.add_checklist_item(
            checklist_id=Id.from_string(command.checklist_id),
            text=command.text,
            assignee_id=assignee_id,
            due_date=item_due_date,
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())
