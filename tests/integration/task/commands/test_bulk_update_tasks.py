"""Интеграционные тесты BulkUpdateTasksHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.bulk_update_tasks import BulkUpdateTasksCommand, BulkUpdateTasksHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.task_priority import TaskPriority


@pytest.mark.integration
class TestBulkUpdateTasksHandler:
    """Тесты массового обновления задач — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, board_stub, sprint_stub, epic_stub, permission_checker_stub, event_bus_stub) -> BulkUpdateTasksHandler:
        return BulkUpdateTasksHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            sprint_port=sprint_stub,
            epic_port=epic_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_bulk_update_priority(self, handler, task_repo, make_task) -> None:
        task1 = await make_task()
        task2 = await make_task()

        cmd = BulkUpdateTasksCommand(
            task_ids=[str(task1.id), str(task2.id)],
            changes={"priority": "high"},
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found1 = await task_repo.get_by_id(task1.id)
        found2 = await task_repo.get_by_id(task2.id)
        assert found1 is not None
        assert found2 is not None
        assert found1.priority == TaskPriority.HIGH
        assert found2.priority == TaskPriority.HIGH

    async def test_bulk_update_sprint(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        sprint_id = Id.generate()

        cmd = BulkUpdateTasksCommand(
            task_ids=[str(task.id)],
            changes={"sprint_id": str(sprint_id)},
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.sprint_id == sprint_id

    async def test_bulk_update_task_not_found(self, handler) -> None:
        cmd = BulkUpdateTasksCommand(
            task_ids=[str(Id.generate())],
            changes={"priority": "high"},
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_bulk_update_permission_denied(self, task_repo, changelog_repo, board_stub, sprint_stub, epic_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = BulkUpdateTasksHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            sprint_port=sprint_stub,
            epic_port=epic_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = BulkUpdateTasksCommand(
            task_ids=[str(task.id)],
            changes={"priority": "high"},
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
