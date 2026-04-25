"""Cross-context: Project outboard adapters — проверка, что данные Project BC
корректно предоставляются другим BC через outboard-порты."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.project_provider_adapter import (
    ProjectProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.project_role_provider_adapter import (
    ProjectRoleProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.board_provider_adapter import (
    BoardProviderAdapter,
)


@pytest.mark.integration
class TestProjectOutboardAdaptersCrossContext:
    """Cross-context: Project outboard adapters предоставляют данные другим BC."""

    async def test_project_provider_returns_project_data(
        self, project_repo, make_project_with_membership,
    ) -> None:
        data = await make_project_with_membership(name="CrossCtx Project")
        adapter = ProjectProviderAdapter(repo=project_repo)

        result = await adapter.get_project(str(data["project"].id))
        assert result is not None
        assert result.name == "CrossCtx Project"

        exists = await adapter.project_exists(str(data["project"].id))
        assert exists is True

    async def test_project_provider_returns_projects_by_workspace(
        self, project_repo, make_project_with_membership,
    ) -> None:
        ws_id = Id.generate()
        await make_project_with_membership(workspace_id=ws_id)
        adapter = ProjectProviderAdapter(repo=project_repo)

        result = await adapter.get_projects_by_workspace(str(ws_id))
        assert len(result) >= 1

    async def test_project_role_provider_returns_roles(
        self, proj_role_repo, make_project_with_membership,
    ) -> None:
        data = await make_project_with_membership()
        adapter = ProjectRoleProviderAdapter(repo=proj_role_repo)

        roles = await adapter.get_roles_by_project(str(data["project"].id))
        assert len(roles) >= 1

    async def test_board_provider_returns_board(
        self, board_repo, make_project_with_membership,
    ) -> None:
        data = await make_project_with_membership()
        adapter = BoardProviderAdapter(repo=board_repo)

        board = await adapter.get_board(str(data["project"].id))
        assert board is not None
        assert board.project_id == str(data["project"].id)

        columns = await adapter.get_columns(str(data["project"].id))
        assert isinstance(columns, list)
