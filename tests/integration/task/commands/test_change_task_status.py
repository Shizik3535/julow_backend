"""Интеграционные тесты ChangeTaskStatusHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.change_task_status import ChangeTaskStatusCommand, ChangeTaskStatusHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_app_exceptions import TaskStatusTransitionNotAllowedException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestChangeTaskStatusHandler:
    """Тесты смены workflow-статуса — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, board_stub, permission_checker_stub, event_bus_stub) -> ChangeTaskStatusHandler:
        return ChangeTaskStatusHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_status_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        new_status_id = Id.generate()
        changed_by = Id.generate()

        cmd = ChangeTaskStatusCommand(
            task_id=str(task.id),
            new_status_id=str(new_status_id),
            changed_by=str(changed_by),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status_id == new_status_id

    async def test_change_status_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        new_status_id = Id.generate()
        changed_by = Id.generate()

        cmd = ChangeTaskStatusCommand(
            task_id=str(task.id),
            new_status_id=str(new_status_id),
            changed_by=str(changed_by),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "status_id")
        assert len(entries) >= 1

    async def test_change_status_task_not_found(self, handler) -> None:
        cmd = ChangeTaskStatusCommand(
            task_id=str(Id.generate()),
            new_status_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_change_status_transition_not_allowed(self, handler, make_task) -> None:
        class _DenyTransitionBoard(handler._board_port.__class__):
            async def is_transition_allowed(self, project_id: str, from_status_id: str, to_status_id: str) -> bool:
                return False

        handler._board_port = _DenyTransitionBoard()

        task = await make_task()
        old_status_id = Id.generate()
        task.change_status(old_status_id)
        task.clear_domain_events()
        from app.context.task.infrastructure.persistence.repositories.sql_task_repository import SqlTaskRepository
        await handler._task_repo.update(task)

        cmd = ChangeTaskStatusCommand(
            task_id=str(task.id),
            new_status_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskStatusTransitionNotAllowedException):
            await handler.handle(cmd)

    async def test_change_status_permission_denied(self, task_repo, changelog_repo, board_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = ChangeTaskStatusHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = ChangeTaskStatusCommand(
            task_id=str(task.id),
            new_status_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
