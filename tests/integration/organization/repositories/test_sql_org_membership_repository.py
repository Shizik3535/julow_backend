"""Интеграционные тесты SqlOrgMembershipRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.entities.org_member import OrgMember
from app.context.organization.infrastructure.persistence.repositories.sql_org_membership_repository import (
    SqlOrgMembershipRepository,
)


@pytest.mark.integration
class TestSqlOrgMembershipRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_org_id(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        found = await membership_repo.get_by_org_id(data["org"].id)
        assert found is not None
        assert found.org_id == data["org"].id

    async def test_add_persists_members(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        found = await membership_repo.get_by_org_id(data["org"].id)
        assert found is not None
        assert len(found.members) >= 1
        assert any(m.user_id == data["owner_id"] for m in found.members)

    async def test_get_by_org_id_not_found(self, membership_repo: SqlOrgMembershipRepository) -> None:
        found = await membership_repo.get_by_org_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlOrgMembershipRepositorySearch:
    """Тесты поиска."""

    async def test_get_member_by_org_and_user_found(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        member = await membership_repo.get_member_by_org_and_user(
            org_id=data["org"].id, user_id=data["owner_id"]
        )
        assert member is not None
        assert member.user_id == data["owner_id"]

    async def test_get_member_by_org_and_user_not_found(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        member = await membership_repo.get_member_by_org_and_user(
            org_id=data["org"].id, user_id=Id.generate()
        )
        assert member is None

    async def test_get_members_by_org(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        members = await membership_repo.get_members_by_org(data["org"].id)
        assert len(members) >= 1


@pytest.mark.integration
class TestSqlOrgMembershipRepositoryUpdate:
    """Тесты обновления дочерних OrgMember."""

    async def test_update_add_member(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        membership = data["membership"]
        new_user_id = Id.generate()
        membership.add_member(
            user_id=new_user_id,
            role_id=data["owner_role"].id,
        )
        membership.clear_domain_events()
        await membership_repo.update(membership)

        found = await membership_repo.get_by_org_id(data["org"].id)
        assert found is not None
        assert any(m.user_id == new_user_id for m in found.members)

    async def test_update_remove_member(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        membership = data["membership"]

        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.remove_member(user_id=new_user_id, is_owner=False)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        found = await membership_repo.get_by_org_id(data["org"].id)
        assert found is not None
        assert not any(m.user_id == new_user_id for m in found.members)

    async def test_update_deactivate_member(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        membership = data["membership"]

        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.deactivate_member(user_id=new_user_id, is_owner=False)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        member = await membership_repo.get_member_by_org_and_user(
            org_id=data["org"].id, user_id=new_user_id
        )
        assert member is not None
        assert member.is_active is False

    async def test_update_change_role(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership, make_org_role
    ) -> None:
        data = await make_org_with_membership()
        membership = data["membership"]

        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=data["owner_role"].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        new_role = await make_org_role(org_id=data["org"].id)
        membership.change_member_role(user_id=new_user_id, new_role_id=new_role.id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        member = await membership_repo.get_member_by_org_and_user(
            org_id=data["org"].id, user_id=new_user_id
        )
        assert member is not None
        assert member.role_id == new_role.id

    async def test_update_display_name(
        self, membership_repo: SqlOrgMembershipRepository, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        membership = data["membership"]

        new_user_id = Id.generate()
        membership.add_member(user_id=new_user_id, role_id=data["owner_role"].id, display_name="Old Name")
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.update_member_display_name(user_id=new_user_id, display_name="New Name")
        membership.clear_domain_events()
        await membership_repo.update(membership)

        member = await membership_repo.get_member_by_org_and_user(
            org_id=data["org"].id, user_id=new_user_id
        )
        assert member is not None
        assert member.display_name == "New Name"
