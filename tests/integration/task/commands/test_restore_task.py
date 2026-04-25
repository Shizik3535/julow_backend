"""Интеграционные тесты RestoreTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.restore_task import RestoreTaskCommand, RestoreTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.task_status import TaskStatus


@pytest.mark.integration
class TestRestoreTaskHandler:
    """Тесты восстановления задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RestoreTaskHandler:
        return RestoreTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_restore_task_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.archive()
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RestoreTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status == TaskStatus.ACTIVE

    async def test_restore_task_not_found(self, handler) -> None:
        cmd = RestoreTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_restore_task_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RestoreTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = RestoreTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
