"""Интеграционные тесты BoardProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.board_provider_adapter import (
    BoardProviderAdapter,
)


@pytest.mark.integration
class TestBoardProviderAdapter:
    """Тесты BoardProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, board_repo) -> BoardProviderAdapter:
        return BoardProviderAdapter(repo=board_repo)

    async def test_get_board_found(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_board(str(data["project"].id))
        assert result is not None
        assert result.project_id == str(data["project"].id)

    async def test_get_board_not_found(self, adapter) -> None:
        result = await adapter.get_board(str(Id.generate()))
        assert result is None

    async def test_get_workflow_statuses(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_workflow_statuses(str(data["project"].id))
        assert isinstance(result, list)

    async def test_get_columns(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_columns(str(data["project"].id))
        assert isinstance(result, list)

    async def test_get_default_status_id(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_default_status_id(str(data["project"].id))
        # May or may not have a default status
        assert result is None or isinstance(result, str)

    async def test_is_transition_allowed_no_board(self, adapter) -> None:
        result = await adapter.is_transition_allowed(
            str(Id.generate()), str(Id.generate()), str(Id.generate()),
        )
        assert result is False
