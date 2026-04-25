"""Интеграционные тесты RemoveBoardSwimlaneHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_board_swimlane import (
    RemoveBoardSwimlaneCommand,
    RemoveBoardSwimlaneHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveBoardSwimlaneHandler:
    """Тесты RemoveBoardSwimlaneHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> RemoveBoardSwimlaneHandler:
        return RemoveBoardSwimlaneHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_swimlane_success(self, handler, board_repo, make_project_with_membership) -> None:
        from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        board.add_swimlane(name="ToDelete", group_by=SwimlaneGroupBy.ASSIGNEE)
        board.clear_domain_events()
        await board_repo.update(board)

        swimlane_id = board.swimlanes[-1].id
        cmd = RemoveBoardSwimlaneCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            swimlane_id=str(swimlane_id),
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_remove_swimlane_board_not_found(self, handler) -> None:
        cmd = RemoveBoardSwimlaneCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            swimlane_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
