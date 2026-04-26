"""Unit-тесты для агрегата WorkspaceTeam (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.events.workspace_team_events import (
    WorkspaceTeamCreated,
    WorkspaceTeamUpdated,
    WorkspaceTeamDeleted,
    WorkspaceTeamMemberAdded,
    WorkspaceTeamMemberRemoved,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamCreation:
    def test_create_team(self, new_team: WorkspaceTeam) -> None:
        assert new_team.name == "TestTeam"
        assert new_team.is_active is True
        assert new_team.member_ids == []

    def test_create_team_emits_created(self, new_team: WorkspaceTeam) -> None:
        events = new_team.clear_domain_events()
        assert any(isinstance(e, WorkspaceTeamCreated) for e in events)

    def test_create_with_lead_adds_lead_to_members(self, any_workspace_id: Id) -> None:
        lead_id = IdFactory()
        team = WorkspaceTeam.create(workspace_id=any_workspace_id, name="TestTeam", lead_id=lead_id)
        assert lead_id in team.member_ids


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamUpdate:
    def test_update_name(self, team: WorkspaceTeam) -> None:
        team.update(name="NewName")
        assert team.name == "NewName"

    def test_update_description(self, team: WorkspaceTeam) -> None:
        team.update(description="New desc")
        assert team.description == "New desc"

    def test_update_lead_id(self, team: WorkspaceTeam) -> None:
        new_lead = IdFactory()
        team.update(lead_id=new_lead)
        assert team.lead_id == new_lead

    def test_update_icon_url(self, team: WorkspaceTeam) -> None:
        url = Url("https://example.com/icon.png")
        team.update(icon_url=url)
        assert team.icon_url == url

    def test_update_emits_event(self, team: WorkspaceTeam) -> None:
        team.update(name="NewName")
        events = team.clear_domain_events()
        event = next(e for e in events if isinstance(e, WorkspaceTeamUpdated))
        assert "name" in event.changed_fields

    def test_update_no_change_no_event(self, team: WorkspaceTeam) -> None:
        team.update(name="TestTeam")
        events = team.clear_domain_events()
        assert not any(isinstance(e, WorkspaceTeamUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Участники
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamMembers:
    def test_add_member(self, team: WorkspaceTeam) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        assert user_id in team.member_ids

    def test_add_member_emits_event(self, team: WorkspaceTeam) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        events = team.clear_domain_events()
        assert any(isinstance(e, WorkspaceTeamMemberAdded) for e in events)

    def test_add_duplicate_member_raises(self, team: WorkspaceTeam) -> None:
        from app.context.workspace.domain.exceptions.workspace_team_exceptions import TeamMemberAlreadyExistsException
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        with pytest.raises(TeamMemberAlreadyExistsException):
            team.add_member(user_id)
        assert team.member_ids.count(user_id) == 1

    def test_add_member_to_inactive_team_raises(self, inactive_team: WorkspaceTeam) -> None:
        with pytest.raises(ValueError):
            inactive_team.add_member(IdFactory())

    def test_remove_member(self, team: WorkspaceTeam) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        team.remove_member(user_id)
        assert user_id not in team.member_ids

    def test_remove_member_emits_event(self, team: WorkspaceTeam) -> None:
        user_id = IdFactory()
        team.add_member(user_id)
        team.clear_domain_events()
        team.remove_member(user_id)
        events = team.clear_domain_events()
        assert any(isinstance(e, WorkspaceTeamMemberRemoved) for e in events)

    def test_remove_nonexistent_member_ignored(self, team: WorkspaceTeam) -> None:
        team.remove_member(IdFactory())
        events = team.clear_domain_events()
        assert not any(isinstance(e, WorkspaceTeamMemberRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTeamStatus:
    def test_deactivate(self, team: WorkspaceTeam) -> None:
        team.deactivate()
        assert team.is_active is False

    def test_deactivate_emits_event(self, team: WorkspaceTeam) -> None:
        team.deactivate()
        events = team.clear_domain_events()
        assert any(isinstance(e, WorkspaceTeamDeleted) for e in events)

    def test_reactivate(self, inactive_team: WorkspaceTeam) -> None:
        inactive_team.reactivate()
        assert inactive_team.is_active is True
