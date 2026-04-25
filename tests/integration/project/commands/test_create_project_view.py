"""Интеграционные тесты CreateProjectViewHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_project_view import (
    CreateProjectViewCommand,
    CreateProjectViewHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateProjectViewHandler:
    """Тесты CreateProjectViewHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> CreateProjectViewHandler:
        return CreateProjectViewHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_view_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]

        cmd = CreateProjectViewCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            name="My View",
            view_type="board",
        )
        await handler.handle(cmd)

        board = await board_repo.get_by_project_id(project.id)
        assert board is not None
        assert any(v.name == "My View" for v in board.views)

    async def test_create_view_board_not_found(self, handler) -> None:
        cmd = CreateProjectViewCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
            view_type="board",
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
