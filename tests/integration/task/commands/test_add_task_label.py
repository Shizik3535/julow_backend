"""Интеграционные тесты AddTaskLabelHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.add_task_label import AddTaskLabelCommand, AddTaskLabelHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException, DuplicateLabelException


@pytest.mark.integration
class TestAddTaskLabelHandler:
    """Тесты добавления метки — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> AddTaskLabelHandler:
        return AddTaskLabelHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_add_label_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = AddTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(task.id), name="frontend")
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert any(l.name == "frontend" for l in found.labels)

    async def test_add_duplicate_label_raises(self, handler, make_task) -> None:
        task = await make_task()
        cmd = AddTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(task.id), name="frontend")
        await handler.handle(cmd)

        with pytest.raises(DuplicateLabelException):
            await handler.handle(cmd)

    async def test_add_label_task_not_found(self, handler) -> None:
        cmd = AddTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(Id.generate()), name="label")
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_label_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AddTaskLabelHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = AddTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(task.id), name="denied")
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
