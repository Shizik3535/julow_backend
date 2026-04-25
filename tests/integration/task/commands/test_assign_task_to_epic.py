"""Интеграционные тесты AssignTaskToEpicHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.assign_task_to_epic import AssignTaskToEpicCommand, AssignTaskToEpicHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_app_exceptions import TaskEpicNotAvailableException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAssignTaskToEpicHandler:
    """Тесты привязки задачи к эпику — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, epic_stub, permission_checker_stub, event_bus_stub) -> AssignTaskToEpicHandler:
        return AssignTaskToEpicHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            epic_port=epic_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_assign_to_epic_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        epic_id = Id.generate()

        cmd = AssignTaskToEpicCommand(
            task_id=str(task.id),
            epic_id=str(epic_id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.epic_id == epic_id

    async def test_assign_to_epic_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        epic_id = Id.generate()

        cmd = AssignTaskToEpicCommand(
            task_id=str(task.id),
            epic_id=str(epic_id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "epic_id")
        assert len(entries) >= 1

    async def test_assign_to_epic_not_found(self, handler) -> None:
        cmd = AssignTaskToEpicCommand(
            task_id=str(Id.generate()),
            epic_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_assign_to_epic_epic_not_available(self, handler, make_task) -> None:
        class _NotFoundEpic(handler._epic_port.__class__):
            async def epic_exists(self, epic_id: str) -> bool:
                return False

        handler._epic_port = _NotFoundEpic()

        task = await make_task()
        cmd = AssignTaskToEpicCommand(
            task_id=str(task.id),
            epic_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskEpicNotAvailableException):
            await handler.handle(cmd)

    async def test_assign_to_epic_permission_denied(self, task_repo, changelog_repo, epic_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AssignTaskToEpicHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            epic_port=epic_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = AssignTaskToEpicCommand(
            task_id=str(task.id),
            epic_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
