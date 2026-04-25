"""Интеграционные тесты SetActualEffortHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.set_actual_effort import SetActualEffortCommand, SetActualEffortHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@pytest.mark.integration
class TestSetActualEffortHandler:
    """Тесты установки фактического усилия — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> SetActualEffortHandler:
        return SetActualEffortHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_set_actual_effort_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        changed_by = Id.generate()
        cmd = SetActualEffortCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=5.0,
            unit="hours",
            changed_by=str(changed_by),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.actual_effort is not None
        assert found.actual_effort.value == 5.0
        assert found.actual_effort.unit == EffortUnit.HOURS

    async def test_set_actual_effort_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        cmd = SetActualEffortCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=3.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "actual_effort")
        assert len(entries) >= 1

    async def test_set_actual_effort_task_not_found(self, handler) -> None:
        cmd = SetActualEffortCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            value=1.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_set_actual_effort_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = SetActualEffortHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = SetActualEffortCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=1.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
