from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.task.application.ports.integration.inboard.project_membership_port import ProjectMembershipPort
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class AssignTaskCommand(BaseCommand):
    """
    Команда назначения исполнителя задачи.

    Атрибуты:
        task_id: ID задачи.
        assignee_id: ID исполнителя.
        changed_by: ID изменившего.
    """

    task_id: str
    assignee_id: str
    changed_by: str


class AssignTaskHandler(BaseCommandHandler[AssignTaskCommand, None]):
    """
    Обработчик назначения исполнителя.

    Проверяет существование пользователя и его участие в проекте.
    """

    REQUIRED_PERMISSION = "tasks.assign"

    def __init__(
        self,
        task_repo: TaskRepository,
        changelog_repo: ChangelogRepository,
        identity_port: IdentityUserPort,
        membership_port: ProjectMembershipPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._changelog_repo = changelog_repo
        self._identity_port = identity_port
        self._membership_port = membership_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AssignTaskCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        # Self-assign разрешен без отдельного права.
        if command.changed_by != command.assignee_id:
            await self._permission_checker.require_permission(
                user_id=command.changed_by,
                project_id=str(task.project_id),
                permission=self.REQUIRED_PERMISSION,
            )

        if not await self._identity_port.user_exists(command.assignee_id):
            raise ValueError(f"Пользователь {command.assignee_id} не найден")

        if not await self._membership_port.is_project_member(str(task.project_id), command.assignee_id):
            raise ValueError(f"Пользователь {command.assignee_id} не является участником проекта")

        task.assign(Id.from_string(command.assignee_id))
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

        entry = ChangelogEntry.create(
            task_id=Id.from_string(command.task_id),
            field_name="assignee",
            old_value=None,
            new_value=command.assignee_id,
            changed_by=Id.from_string(command.changed_by),
        )
        await self._changelog_repo.add(entry)
