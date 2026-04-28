"""Интеграционные тесты SqlTeamRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.infrastructure.persistence.repositories.sql_team_repository import (
    SqlTeamRepository,
)


@pytest.mark.integration
class TestSqlTeamRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team(name="Alpha")
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.id == team.id

    async def test_add_with_lead_adds_member(
        self, team_repo: SqlTeamRepository, make_team, _ensure_user
    ) -> None:
        lead_id = Id.generate()
        await _ensure_user(lead_id)
        team = await make_team(lead_id=lead_id)
        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert lead_id in found.member_ids


@pytest.mark.integration
class TestSqlTeamRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_org(self, team_repo: SqlTeamRepository, make_team, make_org) -> None:
        org = await make_org()
        team = await make_team(org_id=org.id)
        found = await team_repo.get_by_org(org.id)
        assert len(found) >= 1
        assert any(t.id == team.id for t in found)

    async def test_get_by_member(
        self, team_repo: SqlTeamRepository, make_team, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        team = await make_team()
        team.add_member(user_id)
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_member(user_id)
        assert len(found) >= 1
        assert any(t.id == team.id for t in found)

    async def test_get_by_lead(
        self, team_repo: SqlTeamRepository, make_team, _ensure_user
    ) -> None:
        lead_id = Id.generate()
        await _ensure_user(lead_id)
        team = await make_team(lead_id=lead_id)
        found = await team_repo.get_by_lead(lead_id)
        assert len(found) >= 1
        assert any(t.id == team.id for t in found)


@pytest.mark.integration
class TestSqlTeamRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_name(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        team.update(name="UpdatedTeam")
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.name == "UpdatedTeam"

    async def test_update_description(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        team.update(description="New description")
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.description == "New description"

    async def test_update_lead_id(self, team_repo: SqlTeamRepository, make_team, _ensure_user) -> None:
        new_lead = Id.generate()
        await _ensure_user(new_lead)
        team = await make_team()
        team.update(lead_id=new_lead)
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.lead_id == new_lead

    async def test_update_icon(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        team.update(icon="Code")
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.icon is not None
        assert found.icon == "Code"

    async def test_update_add_member(
        self, team_repo: SqlTeamRepository, make_team, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        team = await make_team()
        team.add_member(user_id)
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert user_id in found.member_ids

    async def test_update_remove_member(
        self, team_repo: SqlTeamRepository, make_team, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        team = await make_team()
        team.add_member(user_id)
        team.clear_domain_events()
        await team_repo.update(team)

        team.remove_member(user_id)
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert user_id not in found.member_ids

    async def test_update_deactivate(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        team.deactivate()
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is False

    async def test_update_reactivate(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        team.deactivate()
        team.clear_domain_events()
        await team_repo.update(team)

        team.reactivate()
        team.clear_domain_events()
        await team_repo.update(team)

        found = await team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is True


@pytest.mark.integration
class TestSqlTeamRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, team_repo: SqlTeamRepository, make_team) -> None:
        team = await make_team()
        await team_repo.delete(team.id)
        found = await team_repo.get_by_id(team.id)
        assert found is None
