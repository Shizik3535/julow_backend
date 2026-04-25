"""Интеграционные тесты AddWorkflowTransitionHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_workflow_transition import (
    AddWorkflowTransitionCommand,
    AddWorkflowTransitionHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddWorkflowTransitionHandler:
    """Тесты AddWorkflowTransitionHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> AddWorkflowTransitionHandler:
        return AddWorkflowTransitionHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_workflow_transition_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        if len(board.workflow_statuses) < 2:
            pytest.skip("Board needs at least 2 workflow statuses")

        from_id = board.workflow_statuses[0].id
        to_id = board.workflow_statuses[1].id
        cmd = AddWorkflowTransitionCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            from_status_id=str(from_id),
            to_status_id=str(to_id),
            name="Move",
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_add_workflow_transition_board_not_found(self, handler) -> None:
        cmd = AddWorkflowTransitionCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            from_status_id=str(Id.generate()),
            to_status_id=str(Id.generate()),
            name="X",
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
