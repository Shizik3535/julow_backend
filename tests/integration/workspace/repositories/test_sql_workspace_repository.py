"""Интеграционные тесты SqlWorkspaceRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_repository import SqlWorkspaceRepository


@pytest.mark.integration
class TestSqlWorkspaceRepositoryAdd:
    """Тесты добавления Workspace."""

    async def test_add_and_get_by_id(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.id == ws.id

    async def test_add_persists_attributes(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        owner_id = Id.generate()
        ws = await make_workspace(name="Test WS", owner_id=owner_id, workspace_type=WorkspaceType.ENTERPRISE)
        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.name == "Test WS"
        assert found.workspace_type == WorkspaceType.ENTERPRISE
        assert found.status == WorkspaceStatus.ACTIVE
        assert owner_id in found.owner_ids

    async def test_add_with_organization_id(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        org_id = Id.generate()
        ws = await make_workspace(organization_id=org_id)
        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.organization_id == org_id

    async def test_add_with_parent_workspace_id(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        parent = await make_workspace()
        child = await make_workspace(parent_workspace_id=parent.id)
        found = await ws_repo.get_by_id(child.id)
        assert found is not None
        assert found.parent_workspace_id == parent.id


@pytest.mark.integration
class TestSqlWorkspaceRepositorySearch:
    """Тесты поиска Workspace."""

    async def test_get_by_owner(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        owner_id = Id.generate()
        await make_workspace(owner_id=owner_id)
        await make_workspace(owner_id=owner_id)
        other = await make_workspace()

        result = await ws_repo.get_by_owner(owner_id)
        assert len(result) == 2
        assert all(owner_id in ws.owner_ids for ws in result)

    async def test_get_by_organization(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        org_id = Id.generate()
        await make_workspace(organization_id=org_id)
        await make_workspace(organization_id=org_id)
        await make_workspace()

        result = await ws_repo.get_by_organization(org_id)
        assert len(result) == 2

    async def test_get_by_parent(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        parent = await make_workspace()
        await make_workspace(parent_workspace_id=parent.id)
        await make_workspace(parent_workspace_id=parent.id)

        result = await ws_repo.get_by_parent(parent.id)
        assert len(result) == 2

    async def test_get_children(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        parent = await make_workspace()
        await make_workspace(parent_workspace_id=parent.id)

        result = await ws_repo.get_children(parent.id)
        assert len(result) == 1

    async def test_get_root_workspaces(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        await make_workspace()
        parent = await make_workspace()
        await make_workspace(parent_workspace_id=parent.id)

        result = await ws_repo.get_root_workspaces()
        assert len(result) >= 2

    async def test_search_by_name(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        await make_workspace(name="Alpha Team")
        await make_workspace(name="Beta Squad")

        result = await ws_repo.search(filters={"name": "Alpha"})
        assert len(result) >= 1
        assert any("Alpha" in ws.name for ws in result)

    async def test_search_by_status(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        await make_workspace()

        result = await ws_repo.search(filters={"status": "active"})
        assert len(result) >= 1

    async def test_search_pagination(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        for _ in range(5):
            await make_workspace()

        result = await ws_repo.search(offset=0, limit=2)
        assert len(result) <= 2

    async def test_count_by_organization(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        org_id = Id.generate()
        await make_workspace(organization_id=org_id)
        await make_workspace(organization_id=org_id)

        count = await ws_repo.count_by_organization(org_id)
        assert count == 2

    async def test_get_by_owner_not_found(self, ws_repo: SqlWorkspaceRepository) -> None:
        result = await ws_repo.get_by_owner(Id.generate())
        assert result == []

    async def test_get_by_organization_not_found(self, ws_repo: SqlWorkspaceRepository) -> None:
        result = await ws_repo.get_by_organization(Id.generate())
        assert result == []


@pytest.mark.integration
class TestSqlWorkspaceRepositoryUpdate:
    """Тесты обновления Workspace."""

    async def test_update_name(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        ws.update_info(name="Updated Name")
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.name == "Updated Name"

    async def test_add_owner(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        new_owner = Id.generate()
        ws.add_owner(new_owner)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert new_owner in found.owner_ids

    async def test_archive(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        ws.archive()
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.status == WorkspaceStatus.ARCHIVED

    async def test_suspend(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        ws.suspend(reason="test")
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.status == WorkspaceStatus.SUSPENDED

    async def test_update_security_policy(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy

        ws = await make_workspace()
        new_policy = SecurityPolicy(pin_code_enabled=True, password_enabled=True)
        ws.update_security_policy(new_policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.security_policy.pin_code_enabled is True

    async def test_update_membership_policy(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy

        ws = await make_workspace()
        new_policy = MembershipPolicy(allow_invitation_links=True, max_members=50)
        ws.update_membership_policy(new_policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.membership_policy.max_members == 50

    async def test_update_limits(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits

        ws = await make_workspace()
        new_limits = WorkspaceLimits(max_members=100, max_projects=50)
        ws.update_limits(new_limits)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.limits.max_members == 100


@pytest.mark.integration
class TestSqlWorkspaceRepositoryDelete:
    """Тесты удаления Workspace."""

    async def test_delete(self, ws_repo: SqlWorkspaceRepository, make_workspace) -> None:
        ws = await make_workspace()
        await ws_repo.delete(ws.id)
        found = await ws_repo.get_by_id(ws.id)
        assert found is None

    async def test_delete_not_found_raises(self, ws_repo: SqlWorkspaceRepository) -> None:
        from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            await ws_repo.delete(Id.generate())


@pytest.mark.integration
class TestSqlWorkspaceRepositoryNotFound:
    """Тесты not found."""

    async def test_get_by_id_not_found(self, ws_repo: SqlWorkspaceRepository) -> None:
        found = await ws_repo.get_by_id(Id.generate())
        assert found is None

    async def test_search_empty(self, ws_repo: SqlWorkspaceRepository) -> None:
        result = await ws_repo.search(filters={"name": "nonexistent-xyz"})
        assert result == []
