"""Интеграционные тесты AddBoardColumnHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_board_column import (
    AddBoardColumnCommand,
    AddBoardColumnHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddBoardColumnHandler:
    """Тесты AddBoardColumnHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> AddBoardColumnHandler:
        return AddBoardColumnHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_column_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]

        cmd = AddBoardColumnCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            name="In Progress",
            color="#FF0000",
        )
        await handler.handle(cmd)

        board = await board_repo.get_by_project_id(project.id)
        assert board is not None
        assert any(c.name == "In Progress" for c in board.columns)

    async def test_add_column_board_not_found(self, handler) -> None:
        cmd = AddBoardColumnCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
