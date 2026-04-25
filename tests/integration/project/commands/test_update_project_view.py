"""Интеграционные тесты UpdateProjectViewHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_project_view import (
    UpdateProjectViewCommand,
    UpdateProjectViewHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateProjectViewHandler:
    """Тесты UpdateProjectViewHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> UpdateProjectViewHandler:
        return UpdateProjectViewHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_view_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
        board.create_view(name="Old View", config=ProjectViewConfig())
        board.clear_domain_events()
        await board_repo.update(board)

        view_id = board.views[-1].id
        cmd = UpdateProjectViewCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            view_id=str(view_id),
            name="Updated View",
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_update_view_board_not_found(self, handler) -> None:
        cmd = UpdateProjectViewCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            view_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
