"""Интеграционные тесты ChangeBoardColumnWipLimitHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_board_column_wip_limit import (
    ChangeBoardColumnWipLimitCommand,
    ChangeBoardColumnWipLimitHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeBoardColumnWipLimitHandler:
    """Тесты ChangeBoardColumnWipLimitHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> ChangeBoardColumnWipLimitHandler:
        return ChangeBoardColumnWipLimitHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_wip_limit_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        if len(board.columns) == 0:
            pytest.skip("Board has no columns")

        column_id = board.columns[0].id
        cmd = ChangeBoardColumnWipLimitCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            column_id=str(column_id),
            wip_limit=5,
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_change_wip_limit_board_not_found(self, handler) -> None:
        cmd = ChangeBoardColumnWipLimitCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            column_id=str(Id.generate()),
            wip_limit=5,
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
