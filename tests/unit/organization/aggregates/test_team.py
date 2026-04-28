"""Unit-тесты для агрегата Team (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.domain.exceptions.team_exceptions import TeamMemberAlreadyExistsException
from app.context.organization.domain.events.team_events import (
    TeamCreated,
    TeamUpdated,
    TeamDeleted,
    TeamMemberAdded,
    TeamMemberRemoved,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamCreation:
    def test_create(self, any_org_id: Id) -> None:
        team = Team.create(org_id=any_org_id, name="DevTeam")
        assert team.name == "DevTeam"
        assert team.org_id == any_org_id
        assert team.is_active is True
        assert team.member_ids == []

    def test_create_with_lead_adds_lead_to_members(self, any_org_id: Id) -> None:
        lead_id = IdFactory()
        team = Team.create(org_id=any_org_id, name="DevTeam", lead_id=lead_id)
        assert lead_id in team.member_ids

    def test_create_without_lead(self, any_org_id: Id) -> None:
        team = Team.create(org_id=any_org_id, name="DevTeam")
        assert team.lead_id is None
        assert team.member_ids == []

    def test_create_emits_team_created(self, new_team: Team) -> None:
        events = new_team.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TeamCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamUpdate:
    def test_update_name(self, team: Team) -> None:
        team.update(name="NewName")
        assert team.name == "NewName"

    def test_update_description(self, team: Team) -> None:
        team.update(description="New description")
        assert team.description == "New description"

    def test_update_lead_id(self, team: Team) -> None:
        new_lead = IdFactory()
        team.update(lead_id=new_lead)
        assert team.lead_id == new_lead

    def test_update_icon(self, team: Team) -> None:
        team.update(icon="Code")
        assert team.icon == "Code"

    def test_update_emits_team_updated(self, team: Team) -> None:
        team.update(name="NewName")
        events = team.clear_domain_events()
        assert any(isinstance(e, TeamUpdated) for e in events)

    def test_update_no_change_no_event(self, team: Team) -> None:
        team.update(name="TestTeam")
        events = team.clear_domain_events()
        assert not any(isinstance(e, TeamUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Участники
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamMembers:
    def test_add_member(self, team: Team) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        assert user_id in team.member_ids

    def test_add_member_emits_event(self, team: Team) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        events = team.clear_domain_events()
        assert any(isinstance(e, TeamMemberAdded) for e in events)

    def test_add_duplicate_member_raises(self, team: Team) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        with pytest.raises(TeamMemberAlreadyExistsException):
            team.add_member(user_id)

    def test_add_member_to_inactive_team_raises(self, inactive_team: Team) -> None:
        with pytest.raises(ValueError):
            inactive_team.add_member(IdFactory())

    def test_remove_member(self, team: Team) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        team.remove_member(user_id)
        assert user_id not in team.member_ids

    def test_remove_member_emits_event(self, team: Team) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        team.remove_member(user_id)
        events = team.clear_domain_events()
        assert any(isinstance(e, TeamMemberRemoved) for e in events)

    def test_remove_nonexistent_member_ignored(self, team: Team) -> None:
        team.remove_member(IdFactory())
        events = team.clear_domain_events()
        assert not any(isinstance(e, TeamMemberRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamStatus:
    def test_deactivate(self, team: Team) -> None:
        team.deactivate()
        assert team.is_active is False

    def test_deactivate_emits_team_deleted(self, team: Team) -> None:
        team.deactivate()
        events = team.clear_domain_events()
        assert any(isinstance(e, TeamDeleted) for e in events)

    def test_reactivate(self, inactive_team: Team) -> None:
        inactive_team.reactivate()
        assert inactive_team.is_active is True
