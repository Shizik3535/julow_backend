"""Интеграционные тесты SetTaskRecurrenceHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.set_task_recurrence import SetTaskRecurrenceCommand, SetTaskRecurrenceHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


@pytest.mark.integration
class TestSetTaskRecurrenceHandler:
    """Тесты установки конфигурации повторения — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> SetTaskRecurrenceHandler:
        return SetTaskRecurrenceHandler(task_repo=task_repo, changelog_repo=changelog_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_set_recurrence_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = SetTaskRecurrenceCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            pattern="weekly",
            interval=2,
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.recurrence is not None
        assert found.recurrence.pattern == RecurrencePattern.WEEKLY
        assert found.recurrence.interval == 2

    async def test_set_recurrence_with_end_date(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = SetTaskRecurrenceCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            pattern="daily",
            interval=1,
            end_date="2026-12-31",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.recurrence is not None
        assert found.recurrence.end_date is not None

    async def test_set_recurrence_task_not_found(self, handler) -> None:
        cmd = SetTaskRecurrenceCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            pattern="weekly",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_set_recurrence_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = SetTaskRecurrenceHandler(task_repo=task_repo, changelog_repo=changelog_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = SetTaskRecurrenceCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            pattern="weekly",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
