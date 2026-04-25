from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_exceptions import (
    TaskNotFoundException,
    CircularDependencyException,
)
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.relation_type import RelationType


class AddTaskRelationCommand(BaseCommand):
    """
    Команда добавления связи между задачами.

    Атрибуты:
        task_id: ID задачи.
        related_task_id: ID связанной задачи.
        relation_type: Тип связи.
        created_by: ID создавшего связь.
        caller_id: ID вызывающего команду.
    """

    caller_id: str
    task_id: str
    related_task_id: str
    relation_type: str
    created_by: str


class AddTaskRelationHandler(BaseCommandHandler[AddTaskRelationCommand, None]):
    """
    Обработчик добавления связи.

    Проверяет circular dependency для BLOCKS/IS_BLOCKED_BY.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(self, task_repo: TaskRepository, permission_checker: TaskPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddTaskRelationCommand) -> None:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        related_task = await self._task_repo.get_by_id(Id.from_string(command.related_task_id))
        if related_task is None:
            raise TaskNotFoundException(id=command.related_task_id)

        rel_type = RelationType(command.relation_type)

        if rel_type in (RelationType.BLOCKS, RelationType.IS_BLOCKED_BY):
            await self._check_circular_dependency(
                task_id=command.task_id,
                related_task_id=command.related_task_id,
                relation_type=rel_type,
            )

        task.add_relation(
            related_task_id=Id.from_string(command.related_task_id),
            relation_type=rel_type,
            created_by=Id.from_string(command.created_by),
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())

    async def _check_circular_dependency(
        self, task_id: str, related_task_id: str, relation_type: RelationType
    ) -> None:
        """Обход графа связей для проверки циклической зависимости."""
        visited: set[str] = set()
        queue = [related_task_id]

        blocking_type = (
            RelationType.BLOCKS
            if relation_type == RelationType.BLOCKS
            else RelationType.IS_BLOCKED_BY
        )

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == task_id:
                raise CircularDependencyException()

            current_task = await self._task_repo.get_by_id(Id.from_string(current_id))
            if current_task is None:
                continue

            for rel in current_task.relations:
                if rel.relation_type == blocking_type and str(rel.related_task_id) not in visited:
                    queue.append(str(rel.related_task_id))
