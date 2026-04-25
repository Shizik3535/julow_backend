"""Интеграционные тесты RemoveWorkflowStatusHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_workflow_status import (
    RemoveWorkflowStatusCommand,
    RemoveWorkflowStatusHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveWorkflowStatusHandler:
    """Тесты RemoveWorkflowStatusHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub, event_bus_stub) -> RemoveWorkflowStatusHandler:
        return RemoveWorkflowStatusHandler(
            board_repo=board_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_workflow_status_success(self, handler, board_repo, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        board = data["board"]

        from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory
        board.add_workflow_status(name="ToDelete", category=WorkflowStatusCategory.IN_PROGRESS)
        board.clear_domain_events()
        await board_repo.update(board)

        status_id = board.workflow_statuses[-1].id
        cmd = RemoveWorkflowStatusCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            status_id=str(status_id),
        )
        await handler.handle(cmd)

        found = await board_repo.get_by_id(board.id)
        assert found is not None

    async def test_remove_workflow_status_board_not_found(self, handler) -> None:
        cmd = RemoveWorkflowStatusCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            status_id=str(Id.generate()),
        )
        with pytest.raises(BoardNotFoundException):
            await handler.handle(cmd)
