"""Интеграционные тесты GetBoardHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_board import (
    GetBoardQuery,
    GetBoardHandler,
)
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException


@pytest.mark.integration
class TestGetBoardHandler:
    """Тесты GetBoardHandler."""

    @pytest.fixture
    def handler(self, board_repo, permission_checker_stub) -> GetBoardHandler:
        return GetBoardHandler(board_repo=board_repo, permission_checker=permission_checker_stub)

    async def test_get_board_found(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        project = data["project"]

        query = GetBoardQuery(caller_id=str(Id.generate()), project_id=str(project.id))
        result = await handler.handle(query)
        assert result.project_id == str(project.id)

    async def test_get_board_not_found(self, handler) -> None:
        query = GetBoardQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()))
        with pytest.raises(BoardNotFoundException):
            await handler.handle(query)
