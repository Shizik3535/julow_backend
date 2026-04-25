"""Интеграционные тесты AssignTaskToSprintHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.assign_task_to_sprint import AssignTaskToSprintCommand, AssignTaskToSprintHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_app_exceptions import TaskSprintNotAvailableException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAssignTaskToSprintHandler:
    """Тесты назначения задачи в спринт — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, sprint_stub, permission_checker_stub, event_bus_stub) -> AssignTaskToSprintHandler:
        return AssignTaskToSprintHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            sprint_port=sprint_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_assign_to_sprint_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        sprint_id = Id.generate()

        cmd = AssignTaskToSprintCommand(
            task_id=str(task.id),
            sprint_id=str(sprint_id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.sprint_id == sprint_id

    async def test_assign_to_sprint_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        sprint_id = Id.generate()

        cmd = AssignTaskToSprintCommand(
            task_id=str(task.id),
            sprint_id=str(sprint_id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "sprint_id")
        assert len(entries) >= 1

    async def test_assign_to_sprint_not_found(self, handler) -> None:
        cmd = AssignTaskToSprintCommand(
            task_id=str(Id.generate()),
            sprint_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_assign_to_sprint_sprint_not_available(self, handler, make_task) -> None:
        class _NotFoundSprint(handler._sprint_port.__class__):
            async def sprint_exists(self, sprint_id: str) -> bool:
                return False

        handler._sprint_port = _NotFoundSprint()

        task = await make_task()
        cmd = AssignTaskToSprintCommand(
            task_id=str(task.id),
            sprint_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskSprintNotAvailableException):
            await handler.handle(cmd)

    async def test_assign_to_sprint_permission_denied(self, task_repo, changelog_repo, sprint_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AssignTaskToSprintHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            sprint_port=sprint_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = AssignTaskToSprintCommand(
            task_id=str(task.id),
            sprint_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
