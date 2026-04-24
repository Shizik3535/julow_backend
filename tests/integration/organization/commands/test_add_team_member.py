"""Интеграционные тесты AddTeamMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_team_member import (
    AddTeamMemberCommand,
    AddTeamMemberHandler,
)
from app.context.organization.application.exceptions.membership_app_exceptions import (
    MemberNotInOrganizationException,
)


@pytest.mark.integration
class TestAddTeamMemberHandler:
    @pytest.fixture
    def handler(self, team_repo, membership_repo, permission_checker_stub, event_bus_stub):
        return AddTeamMemberHandler(
            team_repo=team_repo,
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_member(self, handler, make_org_with_membership, make_team, team_repo) -> None:
        data = await make_org_with_membership()
        team = await make_team(org_id=data["org"].id)

        cmd = AddTeamMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            team_id=str(team.id),
            user_id=str(data["owner_id"]),
        )
        await handler.handle(cmd)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert data["owner_id"] in found.member_ids

    async def test_non_org_member_raises(self, handler, make_org, make_team) -> None:
        org = await make_org()
        team = await make_team(org_id=org.id)
        non_member = Id.generate()

        cmd = AddTeamMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            team_id=str(team.id),
            user_id=str(non_member),
        )
        with pytest.raises(MemberNotInOrganizationException):
            await handler.handle(cmd)
