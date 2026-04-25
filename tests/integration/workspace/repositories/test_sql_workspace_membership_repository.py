"""Интеграционные тесты SqlWorkspaceMembershipRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_membership_repository import (
    SqlWorkspaceMembershipRepository,
)


@pytest.mark.integration
class TestSqlWorkspaceMembershipRepositoryAdd:
    """Тесты добавления WorkspaceMembership."""

    async def test_add_and_get_by_id(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        found = await ws_membership_repo.get_by_id(membership.id)
        assert found is not None
        assert found.id == membership.id

    async def test_add_persists_workspace_id(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        assert found.workspace_id == ws.id

    async def test_add_with_owner_member(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        assert len(found.members) == 1
        assert found.members[0].user_id == ws.owner_ids[0]


@pytest.mark.integration
class TestSqlWorkspaceMembershipRepositorySearch:
    """Тесты поиска WorkspaceMembership."""

    async def test_get_by_workspace_id(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None

    async def test_get_by_workspace_id_not_found(self, ws_membership_repo: SqlWorkspaceMembershipRepository) -> None:
        found = await ws_membership_repo.get_by_workspace_id(Id.generate())
        assert found is None

    async def test_get_member_by_workspace_and_user(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        member = await ws_membership_repo.get_member_by_workspace_and_user(ws.id, owner_id)
        assert member is not None
        assert member.user_id == owner_id

    async def test_get_member_by_workspace_and_user_not_found(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        member = await ws_membership_repo.get_member_by_workspace_and_user(ws.id, Id.generate())
        assert member is None

    async def test_get_members_by_workspace(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        members = await ws_membership_repo.get_members_by_workspace(ws.id)
        assert len(members) == 1
        assert members[0].user_id == owner_id


@pytest.mark.integration
class TestSqlWorkspaceMembershipRepositoryUpdate:
    """Тесты обновления WorkspaceMembership (child collection sync)."""

    async def test_add_member(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        new_user_id = Id.generate()
        role_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=role_id, source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        assert len(found.members) == 2

    async def test_remove_member(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        membership.remove_member(new_user_id, is_owner=False)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        assert len(found.members) == 1

    async def test_deactivate_member(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        membership.deactivate_member(new_user_id, is_owner=False)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user_id)
        assert member is not None
        assert member.is_active is False

    async def test_reactivate_member(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.deactivate_member(new_user_id, is_owner=False)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        membership.reactivate_member(new_user_id)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user_id)
        assert member is not None
        assert member.is_active is True

    async def test_change_member_role(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        new_user_id = Id.generate()
        old_role = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=old_role, source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        new_role = Id.generate()
        membership.change_member_role(user_id=new_user_id, new_role_id=new_role)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user_id)
        assert member is not None
        assert member.role_id == new_role

    async def test_add_member_from_org(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        org_user_id = Id.generate()
        role_id = Id.generate()
        membership.add_member_from_org(user_id=org_user_id, role_id=role_id)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(org_user_id)
        assert member is not None
        assert member.source == MemberSource.ORGANIZATION

    async def test_update_member_display_name(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        membership.update_member_display_name(user_id=new_user_id, display_name="New Name")
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user_id)
        assert member is not None
        assert member.display_name == "New Name"


@pytest.mark.integration
class TestSqlWorkspaceMembershipRepositoryDelete:
    """Тесты удаления WorkspaceMembership."""

    async def test_delete(self, ws_membership_repo: SqlWorkspaceMembershipRepository, make_workspace) -> None:
        ws = await make_workspace()
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=ws.owner_ids[0])
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        await ws_membership_repo.delete(membership.id)
        found = await ws_membership_repo.get_by_id(membership.id)
        assert found is None
