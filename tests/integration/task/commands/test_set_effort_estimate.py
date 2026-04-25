"""Интеграционные тесты SetEffortEstimateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.set_effort_estimate import SetEffortEstimateCommand, SetEffortEstimateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.effort_unit import EffortUnit


@pytest.mark.integration
class TestSetEffortEstimateHandler:
    """Тесты установки оценки усилия — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> SetEffortEstimateHandler:
        return SetEffortEstimateHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_set_effort_estimate_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        changed_by = Id.generate()
        cmd = SetEffortEstimateCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=8.0,
            unit="hours",
            changed_by=str(changed_by),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.effort_estimate is not None
        assert found.effort_estimate.value == 8.0
        assert found.effort_estimate.unit == EffortUnit.HOURS

    async def test_set_effort_estimate_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        cmd = SetEffortEstimateCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=5.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "effort_estimate")
        assert len(entries) >= 1

    async def test_set_effort_estimate_task_not_found(self, handler) -> None:
        cmd = SetEffortEstimateCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            value=1.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_set_effort_estimate_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = SetEffortEstimateHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = SetEffortEstimateCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            value=1.0,
            unit="hours",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
