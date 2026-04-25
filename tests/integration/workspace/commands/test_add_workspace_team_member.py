"""Интеграционные тесты AddWorkspaceTeamMemberHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.add_workspace_team_member import (
    AddWorkspaceTeamMemberCommand,
    AddWorkspaceTeamMemberHandler,
)
from app.context.workspace.application.exceptions.membership_app_exceptions import MemberNotInWorkspaceException
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from app.context.workspace.domain.value_objects.member_source import MemberSource
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestAddWorkspaceTeamMemberHandler:
    """Тесты AddWorkspaceTeamMemberHandler."""

    @pytest.fixture
    def handler(self, ws_team_repo, ws_membership_repo) -> AddWorkspaceTeamMemberHandler:
        return AddWorkspaceTeamMemberHandler(
            team_repo=ws_team_repo,
            membership_repo=ws_membership_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_add_team_member_success(
        self, handler, ws_team_repo, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        membership = data["membership"]
        new_user = Id.generate()
        membership.add_member(user_id=new_user, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Team A")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        cmd = AddWorkspaceTeamMemberCommand(
            caller_id=str(ws.owner_ids[0]),
            team_id=str(team.id),
            user_id=str(new_user),
        )
        await handler.handle(cmd)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert new_user in found.member_ids

    async def test_add_team_member_not_workspace_member(
        self, handler, ws_team_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Team B")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        cmd = AddWorkspaceTeamMemberCommand(
            caller_id=str(ws.owner_ids[0]),
            team_id=str(team.id),
            user_id=str(Id.generate()),
        )
        with pytest.raises(MemberNotInWorkspaceException):
            await handler.handle(cmd)

    async def test_team_not_found(self, handler) -> None:
        cmd = AddWorkspaceTeamMemberCommand(
            caller_id=str(Id.generate()),
            team_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceTeamNotFoundException):
            await handler.handle(cmd)
