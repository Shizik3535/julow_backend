"""Интеграционные тесты RemoveBoardColumnHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_board_column import (
    RemoveBoardColumnCommand,
    RemoveBoardColumnHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveBoardColumnHandler:
    """Тесты RemoveBoardColumnHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> RemoveBoardColumnHandler:
        return RemoveBoardColumnHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_column_success(self, handler, board_repo, make_project_with_membership) -> None:
        from app.shared.domain.value_objects.color_vo import Color
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        board.add_column(name="ToDelete", color=Color("#FF0000"))
        board.clear_domain_events()
        await board_repo.update(board)

        column_id = board.columns[-1].id
        cmd = RemoveBoardColumnCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            column_id=str(column_id),
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_remove_column_board_not_found(self, handler) -> None:
        cmd = RemoveBoardColumnCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            column_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
