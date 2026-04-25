"""Интеграционные тесты MoveTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.move_task import MoveTaskCommand, MoveTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestMoveTaskHandler:
    """Тесты перемещения задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, board_stub, permission_checker_stub, event_bus_stub) -> MoveTaskHandler:
        return MoveTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_move_task_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        column_id = Id.generate()

        cmd = MoveTaskCommand(
            task_id=str(task.id),
            column_id=str(column_id),
            position=1.5,
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.order.column_id == column_id
        assert found.order.position == 1.5

    async def test_move_task_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        column_id = Id.generate()

        cmd = MoveTaskCommand(
            task_id=str(task.id),
            column_id=str(column_id),
            position=2.0,
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "column_id")
        assert len(entries) >= 1

    async def test_move_task_not_found(self, handler) -> None:
        cmd = MoveTaskCommand(
            task_id=str(Id.generate()),
            column_id=str(Id.generate()),
            position=1.0,
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_move_task_permission_denied(self, task_repo, changelog_repo, board_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = MoveTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = MoveTaskCommand(
            task_id=str(task.id),
            column_id=str(Id.generate()),
            position=1.0,
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
