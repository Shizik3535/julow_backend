"""Интеграционные тесты RemoveTaskLabelHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_label import RemoveTaskLabelCommand, RemoveTaskLabelHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.label import Label


@pytest.mark.integration
class TestRemoveTaskLabelHandler:
    """Тесты удаления метки — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskLabelHandler:
        return RemoveTaskLabelHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_remove_label_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.add_label(Label(name="frontend", color=None))
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(task.id), label_name="frontend")
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert not any(l.name == "frontend" for l in found.labels)

    async def test_remove_label_task_not_found(self, handler) -> None:
        cmd = RemoveTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(Id.generate()), label_name="label")
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_label_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskLabelHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskLabelCommand(caller_id=str(Id.generate()), task_id=str(task.id), label_name="denied")
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
