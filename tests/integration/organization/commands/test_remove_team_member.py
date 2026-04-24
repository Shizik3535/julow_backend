"""Интеграционные тесты RemoveTeamMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.remove_team_member import (
    RemoveTeamMemberCommand,
    RemoveTeamMemberHandler,
)


@pytest.mark.integration
class TestRemoveTeamMemberHandler:
    @pytest.fixture
    def handler(self, team_repo, permission_checker_stub, event_bus_stub):
        return RemoveTeamMemberHandler(
            team_repo=team_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_member(self, handler, make_org_with_membership, make_team, team_repo) -> None:
        data = await make_org_with_membership()
        team = await make_team(org_id=data["org"].id)
        team.add_member(data["owner_id"])
        team.clear_domain_events()
        await team_repo.update(team)

        cmd = RemoveTeamMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            team_id=str(team.id),
            user_id=str(data["owner_id"]),
        )
        await handler.handle(cmd)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert data["owner_id"] not in found.member_ids
