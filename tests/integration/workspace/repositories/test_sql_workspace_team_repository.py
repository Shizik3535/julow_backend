"""Интеграционные тесты SqlWorkspaceTeamRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_team_repository import (
    SqlWorkspaceTeamRepository,
)


@pytest.mark.integration
class TestSqlWorkspaceTeamRepositoryAdd:
    """Тесты добавления WorkspaceTeam."""

    async def test_add_and_get_by_id(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Dev Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.id == team.id

    async def test_add_with_lead(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        lead_id = Id.generate()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Lead Team", lead_id=lead_id)
        team.clear_domain_events()
        await ws_team_repo.add(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.lead_id == lead_id
        assert lead_id in found.member_ids

    async def test_add_persists_attributes(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Persist Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.name == "Persist Team"
        assert found.workspace_id == ws.id
        assert found.is_active is True


@pytest.mark.integration
class TestSqlWorkspaceTeamRepositorySearch:
    """Тесты поиска WorkspaceTeam."""

    async def test_get_by_workspace(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="WS Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        result = await ws_team_repo.get_by_workspace(ws.id)
        assert len(result) >= 1
        assert any(t.id == team.id for t in result)

    async def test_get_by_member(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        member_id = Id.generate()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Member Team")
        team.add_member(member_id)
        team.clear_domain_events()
        await ws_team_repo.add(team)

        result = await ws_team_repo.get_by_member(member_id)
        assert len(result) >= 1

    async def test_get_by_lead(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        lead_id = Id.generate()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Lead Team", lead_id=lead_id)
        team.clear_domain_events()
        await ws_team_repo.add(team)

        result = await ws_team_repo.get_by_lead(lead_id)
        assert len(result) >= 1

    async def test_get_by_workspace_empty(self, ws_team_repo: SqlWorkspaceTeamRepository) -> None:
        result = await ws_team_repo.get_by_workspace(Id.generate())
        assert result == []


@pytest.mark.integration
class TestSqlWorkspaceTeamRepositoryUpdate:
    """Тесты обновления WorkspaceTeam."""

    async def test_add_member(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Add Member Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        member_id = Id.generate()
        team.add_member(member_id)
        team.clear_domain_events()
        await ws_team_repo.update(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert member_id in found.member_ids

    async def test_remove_member(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        member_id = Id.generate()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Remove Member Team")
        team.add_member(member_id)
        team.clear_domain_events()
        await ws_team_repo.add(team)

        team.remove_member(member_id)
        team.clear_domain_events()
        await ws_team_repo.update(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert member_id not in found.member_ids

    async def test_deactivate(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Deactivate Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        team.deactivate()
        team.clear_domain_events()
        await ws_team_repo.update(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is False

    async def test_reactivate(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Reactivate Team")
        team.deactivate()
        team.clear_domain_events()
        await ws_team_repo.add(team)

        team.reactivate()
        team.clear_domain_events()
        await ws_team_repo.update(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.is_active is True

    async def test_update_info(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Old Name")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        team.update(name="New Name", description="Updated desc")
        team.clear_domain_events()
        await ws_team_repo.update(team)

        found = await ws_team_repo.get_by_id(team.id)
        assert found is not None
        assert found.name == "New Name"
        assert found.description == "Updated desc"


@pytest.mark.integration
class TestSqlWorkspaceTeamRepositoryDelete:
    """Тесты удаления WorkspaceTeam."""

    async def test_delete(self, ws_team_repo: SqlWorkspaceTeamRepository, make_workspace) -> None:
        ws = await make_workspace()
        team = WorkspaceTeam.create(workspace_id=ws.id, name="Delete Team")
        team.clear_domain_events()
        await ws_team_repo.add(team)

        await ws_team_repo.delete(team.id)
        found = await ws_team_repo.get_by_id(team.id)
        assert found is None
