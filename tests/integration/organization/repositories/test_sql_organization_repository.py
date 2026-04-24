"""Интеграционные тесты SqlOrganizationRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.value_objects.org_status import OrgStatus
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy
from app.context.organization.infrastructure.persistence.repositories.sql_organization_repository import (
    SqlOrganizationRepository,
)


@pytest.mark.integration
class TestSqlOrganizationRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.id == org.id

    async def test_add_persists_attributes(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org(name="TestOrg")
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.name == "TestOrg"
        assert found.status == OrgStatus.ACTIVE
        assert isinstance(found.personalization, OrgPersonalization)
        assert isinstance(found.security_policy, SecurityPolicy)
        assert isinstance(found.membership_policy, MembershipPolicy)

    async def test_add_persists_owner_ids(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        owner_id = Id.generate()
        org = await make_org(owner_id=owner_id)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert owner_id in found.owner_ids

    async def test_get_by_id_not_found(self, org_repo: SqlOrganizationRepository) -> None:
        found = await org_repo.get_by_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlOrganizationRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_owner_found(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        owner_id = Id.generate()
        org = await make_org(owner_id=owner_id)
        found = await org_repo.get_by_owner(owner_id)
        assert len(found) >= 1
        assert any(o.id == org.id for o in found)

    async def test_get_by_owner_not_found(self, org_repo: SqlOrganizationRepository) -> None:
        found = await org_repo.get_by_owner(Id.generate())
        assert found == []

    async def test_search_by_name(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        unique_name = f"searchable-{id(self)}"
        await make_org(name=unique_name)
        results = await org_repo.search(filters={"name": unique_name})
        assert len(results) >= 1
        assert any(r.name == unique_name for r in results)

    async def test_search_by_status(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        await make_org()
        results = await org_repo.search(filters={"status": "active"})
        assert len(results) >= 1

    async def test_search_no_filters(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        await make_org()
        results = await org_repo.search()
        assert len(results) >= 1


@pytest.mark.integration
class TestSqlOrganizationRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_name(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        org.update_info(name="UpdatedName")
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.name == "UpdatedName"

    async def test_update_status_suspend(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        org.suspend(reason="test")
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.status == OrgStatus.SUSPENDED

    async def test_update_status_reactivate(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        org.suspend(reason="test")
        org.clear_domain_events()
        await org_repo.update(org)

        org.reactivate()
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.status == OrgStatus.ACTIVE

    async def test_update_owner_ids_add(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        new_owner = Id.generate()
        org.add_owner(new_owner)
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert new_owner in found.owner_ids

    async def test_update_owner_ids_remove(
        self, org_repo: SqlOrganizationRepository, make_org
    ) -> None:
        owner1 = Id.generate()
        owner2 = Id.generate()
        org = await make_org(owner_id=owner1)
        org.add_owner(owner2)
        org.clear_domain_events()
        await org_repo.update(org)

        org.remove_owner(owner2)
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert owner2 not in found.owner_ids
        assert owner1 in found.owner_ids

    async def test_update_security_policy(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        new_policy = SecurityPolicy(require_2fa=True, password_min_length=12)
        org.update_security_policy(new_policy)
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.security_policy.require_2fa is True
        assert found.security_policy.password_min_length == 12

    async def test_update_membership_policy(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        new_policy = MembershipPolicy(max_members=50, require_approval=True)
        org.update_membership_policy(new_policy)
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.membership_policy.max_members == 50
        assert found.membership_policy.require_approval is True

    async def test_update_personalization(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        new_pers = OrgPersonalization(display_name="My Org")
        org.update_info(personalization=new_pers)
        org.clear_domain_events()
        await org_repo.update(org)

        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.personalization.display_name == "My Org"


@pytest.mark.integration
class TestSqlOrganizationRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, org_repo: SqlOrganizationRepository, make_org) -> None:
        org = await make_org()
        await org_repo.delete(org.id)
        found = await org_repo.get_by_id(org.id)
        assert found is None
