"""Интеграционные тесты ChangeTaskTypeHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.change_task_type import ChangeTaskTypeCommand, ChangeTaskTypeHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.task_type import TaskType


@pytest.mark.integration
class TestChangeTaskTypeHandler:
    """Тесты смены типа задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> ChangeTaskTypeHandler:
        return ChangeTaskTypeHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_type_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = ChangeTaskTypeCommand(
            task_id=str(task.id),
            new_type="bug",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.task_type == TaskType.BUG

    async def test_change_type_task_not_found(self, handler) -> None:
        cmd = ChangeTaskTypeCommand(
            task_id=str(Id.generate()),
            new_type="bug",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_change_type_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = ChangeTaskTypeHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = ChangeTaskTypeCommand(
            task_id=str(task.id),
            new_type="bug",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
