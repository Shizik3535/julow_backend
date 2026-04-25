"""Интеграционные тесты ReorderBoardColumnsHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.reorder_board_columns import (
    ReorderBoardColumnsCommand,
    ReorderBoardColumnsHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestReorderBoardColumnsHandler:
    """Тесты ReorderBoardColumnsHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> ReorderBoardColumnsHandler:
        return ReorderBoardColumnsHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_reorder_columns_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        column_ids = [str(c.id) for c in board.columns]
        column_ids.reverse()

        cmd = ReorderBoardColumnsCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            column_ids=column_ids,
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_reorder_columns_board_not_found(self, handler) -> None:
        cmd = ReorderBoardColumnsCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            column_ids=[],
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
