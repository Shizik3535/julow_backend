"""Интеграционные тесты RemoveTaskRecurrenceHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_recurrence import RemoveTaskRecurrenceCommand, RemoveTaskRecurrenceHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


@pytest.mark.integration
class TestRemoveTaskRecurrenceHandler:
    """Тесты удаления конфигурации повторения — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskRecurrenceHandler:
        return RemoveTaskRecurrenceHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_remove_recurrence_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.set_recurrence(RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=1))
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskRecurrenceCommand(caller_id=str(Id.generate()), task_id=str(task.id))
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.recurrence is None

    async def test_remove_recurrence_task_not_found(self, handler) -> None:
        cmd = RemoveTaskRecurrenceCommand(caller_id=str(Id.generate()), task_id=str(Id.generate()))
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_recurrence_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskRecurrenceHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskRecurrenceCommand(caller_id=str(Id.generate()), task_id=str(task.id))
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
