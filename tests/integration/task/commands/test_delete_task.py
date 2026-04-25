"""Интеграционные тесты DeleteTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.delete_task import DeleteTaskCommand, DeleteTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.task_status import TaskStatus


@pytest.mark.integration
class TestDeleteTaskHandler:
    """Тесты soft-delete задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> DeleteTaskHandler:
        return DeleteTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_delete_task_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = DeleteTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status == TaskStatus.DELETED

    async def test_delete_task_not_found(self, handler) -> None:
        cmd = DeleteTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_delete_task_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = DeleteTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = DeleteTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
