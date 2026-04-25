"""Unit-тесты для агрегата Organization (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.org_branding import OrgBranding
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization
from app.context.organization.domain.value_objects.org_status import OrgStatus
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy
from app.context.organization.domain.events.organization_events import (
    OrganizationCreated,
    OrganizationInfoChanged,
    OrganizationSuspended,
    OrganizationReactivated,
    OrganizationDeletionRequested,
    OwnershipTransferred,
    OrgPersonalizationChanged,
    SecurityPolicyChanged,
    MembershipPolicyChanged,
)
from app.context.organization.domain.exceptions.organization_exceptions import (
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    OrganizationAlreadyActiveException,
    OrganizationAlreadySuspendedException,
    OrganizationSuspendedException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationCreation:
    def test_create_with_owner(self, any_owner_id: Id) -> None:
        org = Organization.create(name="TestOrg", owner_id=any_owner_id)
        assert org.name == "TestOrg"
        assert any_owner_id in org.owner_ids
        assert org.status == OrgStatus.ACTIVE

    def test_create_sets_status_active(self, new_organization: Organization) -> None:
        assert new_organization.status == OrgStatus.ACTIVE

    def test_create_emits_organization_created(self, new_organization: Organization) -> None:
        events = new_organization.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], OrganizationCreated)
        assert events[0].name == "TestOrg"

    def test_create_sets_name(self, any_owner_id: Id) -> None:
        org = Organization.create(name="MyOrg", owner_id=any_owner_id)
        assert org.name == "MyOrg"


# ═══════════════════════════════════════════════════════════════════════════
# Обновление информации
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationUpdateInfo:
    def test_update_name(self, organization: Organization) -> None:
        organization.update_info(name="NewName")
        assert organization.name == "NewName"

    def test_update_name_emits_info_changed(self, organization: Organization) -> None:
        organization.update_info(name="NewName")
        events = organization.clear_domain_events()
        assert any(isinstance(e, OrganizationInfoChanged) for e in events)

    def test_update_personalization(self, organization: Organization) -> None:
        pers = OrgPersonalization(display_name="Display")
        organization.update_info(personalization=pers)
        assert organization.personalization.display_name == "Display"

    def test_update_personalization_emits_personalization_changed(self, organization: Organization) -> None:
        pers = OrgPersonalization(display_name="Display")
        organization.update_info(personalization=pers)
        events = organization.clear_domain_events()
        assert any(isinstance(e, OrgPersonalizationChanged) for e in events)

    def test_update_no_change_no_event(self, organization: Organization) -> None:
        organization.update_info(name="TestOrg")
        events = organization.clear_domain_events()
        assert not any(isinstance(e, OrganizationInfoChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Владельцы
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationOwners:
    def test_add_owner(self, organization: Organization) -> None:
        new_owner = IdFactory()
        organization.add_owner(new_owner)
        assert new_owner in organization.owner_ids

    def test_add_duplicate_owner_ignored(self, organization: Organization, any_owner_id: Id) -> None:
        organization.add_owner(any_owner_id)
        assert organization.owner_ids.count(any_owner_id) == 1

    def test_remove_owner(self, organization: Organization) -> None:
        co_owner = IdFactory()
        organization.add_owner(co_owner)
        organization.remove_owner(co_owner)
        assert co_owner not in organization.owner_ids

    def test_remove_last_owner_raises(self, organization: Organization) -> None:
        with pytest.raises(CannotRemoveLastOwnerException):
            organization.remove_owner(organization.owner_ids[0])

    def test_transfer_ownership(self, organization: Organization) -> None:
        old_owner = organization.owner_ids[0]
        new_owner = IdFactory()
        organization.transfer_ownership(old_owner, new_owner)
        assert old_owner not in organization.owner_ids
        assert new_owner in organization.owner_ids

    def test_transfer_ownership_from_non_owner_raises(self, organization: Organization) -> None:
        non_owner = IdFactory()
        new_owner = IdFactory()
        with pytest.raises(CannotTransferOwnershipException):
            organization.transfer_ownership(non_owner, new_owner)

    def test_transfer_ownership_to_existing_owner_raises(self, organization: Organization) -> None:
        old_owner = organization.owner_ids[0]
        with pytest.raises(CannotTransferOwnershipException):
            organization.transfer_ownership(old_owner, old_owner)

    def test_transfer_ownership_emits_event(self, organization: Organization) -> None:
        old_owner = organization.owner_ids[0]
        new_owner = IdFactory()
        organization.transfer_ownership(old_owner, new_owner)
        events = organization.clear_domain_events()
        assert any(isinstance(e, OwnershipTransferred) for e in events)
        event = next(e for e in events if isinstance(e, OwnershipTransferred))
        assert event.old_owner_id == str(old_owner)
        assert event.new_owner_id == str(new_owner)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationStatus:
    def test_suspend(self, organization: Organization) -> None:
        organization.suspend("violation")
        assert organization.status == OrgStatus.SUSPENDED

    def test_suspend_emits_event(self, organization: Organization) -> None:
        organization.suspend("violation")
        events = organization.clear_domain_events()
        assert any(isinstance(e, OrganizationSuspended) for e in events)

    def test_suspend_already_suspended_raises(self, suspended_organization: Organization) -> None:
        with pytest.raises(OrganizationAlreadySuspendedException):
            suspended_organization.suspend("again")

    def test_suspend_when_pending_deletion_raises(self, pending_deletion_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            pending_deletion_organization.suspend("reason")

    def test_reactivate(self, suspended_organization: Organization) -> None:
        suspended_organization.reactivate()
        assert suspended_organization.status == OrgStatus.ACTIVE

    def test_reactivate_emits_event(self, suspended_organization: Organization) -> None:
        suspended_organization.reactivate()
        events = suspended_organization.clear_domain_events()
        assert any(isinstance(e, OrganizationReactivated) for e in events)

    def test_reactivate_not_suspended_raises(self, organization: Organization) -> None:
        with pytest.raises(OrganizationAlreadyActiveException):
            organization.reactivate()

    def test_request_deletion(self, organization: Organization) -> None:
        organization.request_deletion()
        assert organization.status == OrgStatus.PENDING_DELETION

    def test_request_deletion_emits_event(self, organization: Organization) -> None:
        organization.request_deletion()
        events = organization.clear_domain_events()
        assert any(isinstance(e, OrganizationDeletionRequested) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Блокировка операций
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationSuspendedBlocksOps:
    def test_update_info_when_suspended_raises(self, suspended_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            suspended_organization.update_info(name="New")

    def test_add_owner_when_suspended_raises(self, suspended_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            suspended_organization.add_owner(IdFactory())

    def test_remove_owner_when_suspended_raises(self, suspended_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            suspended_organization.remove_owner(suspended_organization.owner_ids[0])

    def test_transfer_ownership_when_suspended_raises(self, suspended_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            suspended_organization.transfer_ownership(suspended_organization.owner_ids[0], IdFactory())

    def test_update_info_when_pending_deletion_raises(self, pending_deletion_organization: Organization) -> None:
        with pytest.raises(OrganizationSuspendedException):
            pending_deletion_organization.update_info(name="New")


# ═══════════════════════════════════════════════════════════════════════════
# Политики
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOrganizationPolicies:
    def test_update_security_policy(self, organization: Organization) -> None:
        policy = SecurityPolicy(require_2fa=True, password_min_length=12)
        organization.update_security_policy(policy)
        assert organization.security_policy.require_2fa is True

    def test_update_security_policy_emits_event(self, organization: Organization) -> None:
        policy = SecurityPolicy(require_2fa=True, password_min_length=12)
        organization.update_security_policy(policy)
        events = organization.clear_domain_events()
        assert any(isinstance(e, SecurityPolicyChanged) for e in events)

    def test_update_security_policy_no_change_no_event(self, organization: Organization) -> None:
        policy = SecurityPolicy()
        organization.update_security_policy(policy)
        events = organization.clear_domain_events()
        assert not any(isinstance(e, SecurityPolicyChanged) for e in events)

    def test_update_membership_policy(self, organization: Organization) -> None:
        policy = MembershipPolicy(require_approval=True, max_members=50)
        organization.update_membership_policy(policy)
        assert organization.membership_policy.require_approval is True

    def test_update_membership_policy_emits_event(self, organization: Organization) -> None:
        policy = MembershipPolicy(require_approval=True, max_members=50)
        organization.update_membership_policy(policy)
        events = organization.clear_domain_events()
        assert any(isinstance(e, MembershipPolicyChanged) for e in events)

    def test_update_membership_policy_no_change_no_event(self, organization: Organization) -> None:
        policy = MembershipPolicy()
        organization.update_membership_policy(policy)
        events = organization.clear_domain_events()
        assert not any(isinstance(e, MembershipPolicyChanged) for e in events)
