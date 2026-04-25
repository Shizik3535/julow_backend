"""Интеграционные тесты UpdateTaskProgressHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.update_task_progress import UpdateTaskProgressCommand, UpdateTaskProgressHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestUpdateTaskProgressHandler:
    """Тесты обновления прогресса — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> UpdateTaskProgressHandler:
        return UpdateTaskProgressHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_update_progress_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = UpdateTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(task.id), progress=75)
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.progress.value == 75

    async def test_update_progress_task_not_found(self, handler) -> None:
        cmd = UpdateTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(Id.generate()), progress=50)
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_update_progress_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = UpdateTaskProgressHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = UpdateTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(task.id), progress=50)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
