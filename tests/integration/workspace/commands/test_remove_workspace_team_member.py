"""Интеграционные тесты RemoveWorkspaceTeamMemberHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.remove_workspace_team_member import (
    RemoveWorkspaceTeamMemberCommand,
    RemoveWorkspaceTeamMemberHandler,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestRemoveWorkspaceTeamMemberHandler:
    """Тесты RemoveWorkspaceTeamMemberHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo) -> RemoveWorkspaceTeamMemberHandler:
        return RemoveWorkspaceTeamMemberHandler(
            team_repo=ws_team_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_remove_team_member_success(self, handler, ws_team_repo, make_workspace_team) -> None:
        member_id = Id.generate()
        team = await make_workspace_team()
        team.add_member(member_id)
        team.clear_domain_events()
        await ws_team_repo.update(team)

        cmd = RemoveWorkspaceTeamMemberCommand(
            caller_id=str(Id.generate()),
            team_id=str(team.id),
            user_id=str(member_id),
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert member_id not in found.member_ids

    async def test_team_not_found(self, handler) -> None:
        cmd = RemoveWorkspaceTeamMemberCommand(
            caller_id=str(Id.generate()),
            team_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(cmd)
