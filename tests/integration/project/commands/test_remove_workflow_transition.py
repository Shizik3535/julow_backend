"""Интеграционные тесты RemoveWorkflowTransitionHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_workflow_transition import (
    RemoveWorkflowTransitionCommand,
    RemoveWorkflowTransitionHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveWorkflowTransitionHandler:
    """Тесты RemoveWorkflowTransitionHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> RemoveWorkflowTransitionHandler:
        return RemoveWorkflowTransitionHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_workflow_transition_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        if len(board.workflow_transitions) == 0:
            pytest.skip("Board has no workflow transitions")

        transition_id = board.workflow_transitions[0].id
        cmd = RemoveWorkflowTransitionCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            transition_id=str(transition_id),
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_remove_workflow_transition_board_not_found(self, handler) -> None:
        cmd = RemoveWorkflowTransitionCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            transition_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
