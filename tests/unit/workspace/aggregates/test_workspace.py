"""Unit-тесты для агрегата Workspace (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.domain.value_objects.workspace_personalization import WorkspacePersonalization
from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits
from app.context.workspace.domain.events.workspace_events import (
    WorkspaceCreated,
    WorkspaceInfoChanged,
    WorkspaceArchived,
    WorkspaceRestored,
    WorkspaceSuspended,
    WorkspaceReactivated,
    WorkspaceDeletionRequested,
    OwnershipTransferred,
    WorkspacePersonalizationChanged,
    SecurityPolicyChanged,
    MembershipPolicyChanged,
    WorkspaceLimitsChanged,
    ChildWorkspaceCreated,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    WorkspaceSuspendedException,
    WorkspaceArchivedException,
    WorkspaceAlreadyArchivedException,
    WorkspaceNotArchivedException,
    WorkspaceAlreadySuspendedException,
    WorkspaceNotSuspendedException,
    WorkspaceDeletionAlreadyRequestedException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceCreation:
    def test_create_with_defaults(self, new_workspace: Workspace, any_owner_id: Id) -> None:
        assert new_workspace.name == "TestWS"
        assert new_workspace.status == WorkspaceStatus.ACTIVE
        assert new_workspace.workspace_type == WorkspaceType.TEAM
        assert any_owner_id in new_workspace.owner_ids

    def test_create_sets_owner(self, new_workspace: Workspace, any_owner_id: Id) -> None:
        assert new_workspace.owner_ids == [any_owner_id]

    def test_create_emits_workspace_created(self, new_workspace: Workspace) -> None:
        events = new_workspace.clear_domain_events()
        created = next(e for e in events if isinstance(e, WorkspaceCreated))
        assert created.name == "TestWS"
        assert created.workspace_type == WorkspaceType.TEAM

    def test_create_with_parent_emits_child_workspace_created(self, any_owner_id: Id) -> None:
        parent_id = IdFactory()
        ws = Workspace.create(
            name="ChildWS",
            owner_id=any_owner_id,
            workspace_type=WorkspaceType.TEAM,
            parent_workspace_id=parent_id,
        )
        events = ws.clear_domain_events()
        assert any(isinstance(e, ChildWorkspaceCreated) for e in events)
        child_event = next(e for e in events if isinstance(e, ChildWorkspaceCreated))
        assert child_event.parent_workspace_id == str(parent_id)

    def test_create_without_parent_no_child_event(self, new_workspace: Workspace) -> None:
        events = new_workspace.clear_domain_events()
        assert not any(isinstance(e, ChildWorkspaceCreated) for e in events)

    def test_create_with_organization(self, any_owner_id: Id) -> None:
        org_id = IdFactory()
        ws = Workspace.create(
            name="OrgWS",
            owner_id=any_owner_id,
            workspace_type=WorkspaceType.ENTERPRISE,
            organization_id=org_id,
        )
        events = ws.clear_domain_events()
        created = next(e for e in events if isinstance(e, WorkspaceCreated))
        assert created.organization_id == str(org_id)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление информации
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceUpdateInfo:
    def test_update_name(self, workspace: Workspace) -> None:
        workspace.update_info(name="NewName")
        assert workspace.name == "NewName"

    def test_update_name_emits_info_changed(self, workspace: Workspace) -> None:
        workspace.update_info(name="NewName")
        events = workspace.clear_domain_events()
        info_event = next(e for e in events if isinstance(e, WorkspaceInfoChanged))
        assert "name" in info_event.changed_fields

    def test_update_personalization(self, workspace: Workspace) -> None:
        pers = WorkspacePersonalization(display_name="My WS")
        workspace.update_info(personalization=pers)
        assert workspace.personalization.display_name == "My WS"

    def test_update_personalization_emits_personalization_changed(self, workspace: Workspace) -> None:
        pers = WorkspacePersonalization(display_name="My WS")
        workspace.update_info(personalization=pers)
        events = workspace.clear_domain_events()
        assert any(isinstance(e, WorkspacePersonalizationChanged) for e in events)

    def test_update_no_change_no_event(self, workspace: Workspace) -> None:
        workspace.update_info(name="TestWS")
        events = workspace.clear_domain_events()
        assert not any(isinstance(e, WorkspaceInfoChanged) for e in events)

    def test_update_name_and_personalization_together(self, workspace: Workspace) -> None:
        pers = WorkspacePersonalization(display_name="Display")
        workspace.update_info(name="NewName", personalization=pers)
        events = workspace.clear_domain_events()
        info_event = next(e for e in events if isinstance(e, WorkspaceInfoChanged))
        assert "name" in info_event.changed_fields


# ═══════════════════════════════════════════════════════════════════════════
# Владельцы
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceOwners:
    def test_add_owner(self, workspace: Workspace) -> None:
        new_owner = IdFactory()
        workspace.add_owner(new_owner)
        assert new_owner in workspace.owner_ids

    def test_add_duplicate_owner_ignored(self, workspace: Workspace, any_owner_id: Id) -> None:
        workspace.add_owner(any_owner_id)
        assert workspace.owner_ids.count(any_owner_id) == 1

    def test_remove_owner(self, workspace: Workspace, any_owner_id: Id) -> None:
        co_owner = IdFactory()
        workspace.add_owner(co_owner)
        workspace.remove_owner(co_owner)
        assert co_owner not in workspace.owner_ids

    def test_remove_last_owner_raises(self, workspace: Workspace) -> None:
        with pytest.raises(CannotRemoveLastOwnerException):
            workspace.remove_owner(workspace.owner_ids[0])

    def test_transfer_ownership(self, workspace: Workspace, any_owner_id: Id) -> None:
        new_owner = IdFactory()
        workspace.transfer_ownership(from_id=any_owner_id, to_id=new_owner)
        assert any_owner_id not in workspace.owner_ids
        assert new_owner in workspace.owner_ids

    def test_transfer_ownership_emits_event(self, workspace: Workspace, any_owner_id: Id) -> None:
        new_owner = IdFactory()
        workspace.transfer_ownership(from_id=any_owner_id, to_id=new_owner)
        events = workspace.clear_domain_events()
        event = next(e for e in events if isinstance(e, OwnershipTransferred))
        assert event.old_owner_id == str(any_owner_id)
        assert event.new_owner_id == str(new_owner)

    def test_transfer_from_non_owner_raises(self, workspace: Workspace) -> None:
        non_owner = IdFactory()
        with pytest.raises(CannotTransferOwnershipException):
            workspace.transfer_ownership(from_id=non_owner, to_id=IdFactory())

    def test_transfer_to_existing_owner_raises(self, workspace: Workspace, any_owner_id: Id) -> None:
        with pytest.raises(CannotTransferOwnershipException):
            workspace.transfer_ownership(from_id=any_owner_id, to_id=any_owner_id)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceStatus:
    def test_archive(self, workspace: Workspace) -> None:
        workspace.archive()
        assert workspace.status == WorkspaceStatus.ARCHIVED

    def test_archive_emits_event(self, workspace: Workspace) -> None:
        workspace.archive()
        events = workspace.clear_domain_events()
        assert any(isinstance(e, WorkspaceArchived) for e in events)

    def test_restore_from_archive(self, archived_workspace: Workspace) -> None:
        archived_workspace.restore()
        assert archived_workspace.status == WorkspaceStatus.ACTIVE

    def test_restore_emits_event(self, archived_workspace: Workspace) -> None:
        archived_workspace.restore()
        events = archived_workspace.clear_domain_events()
        assert any(isinstance(e, WorkspaceRestored) for e in events)

    def test_restore_non_archived_raises(self, workspace: Workspace) -> None:
        with pytest.raises(WorkspaceNotArchivedException):
            workspace.restore()

    def test_suspend(self, workspace: Workspace) -> None:
        workspace.suspend("violation")
        assert workspace.status == WorkspaceStatus.SUSPENDED

    def test_suspend_emits_event(self, workspace: Workspace) -> None:
        workspace.suspend("violation")
        events = workspace.clear_domain_events()
        event = next(e for e in events if isinstance(e, WorkspaceSuspended))
        assert event.reason == "violation"

    def test_suspend_already_suspended_raises(self, suspended_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceAlreadySuspendedException):
            suspended_workspace.suspend("another")

    def test_reactivate(self, suspended_workspace: Workspace) -> None:
        suspended_workspace.reactivate()
        assert suspended_workspace.status == WorkspaceStatus.ACTIVE

    def test_reactivate_emits_event(self, suspended_workspace: Workspace) -> None:
        suspended_workspace.reactivate()
        events = suspended_workspace.clear_domain_events()
        assert any(isinstance(e, WorkspaceReactivated) for e in events)

    def test_reactivate_non_suspended_raises(self, workspace: Workspace) -> None:
        with pytest.raises(WorkspaceNotSuspendedException):
            workspace.reactivate()

    def test_request_deletion(self, workspace: Workspace) -> None:
        workspace.request_deletion()
        assert workspace.status == WorkspaceStatus.PENDING_DELETION

    def test_request_deletion_emits_event(self, workspace: Workspace) -> None:
        workspace.request_deletion()
        events = workspace.clear_domain_events()
        assert any(isinstance(e, WorkspaceDeletionRequested) for e in events)

    def test_request_deletion_already_requested_raises(self, pending_deletion_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceDeletionAlreadyRequestedException):
            pending_deletion_workspace.request_deletion()

    def test_archive_already_archived_raises(self, archived_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceAlreadyArchivedException):
            archived_workspace.archive()


# ═══════════════════════════════════════════════════════════════════════════
# Инварианты статуса
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceStatusInvariants:
    def test_modify_when_suspended_raises(self, suspended_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            suspended_workspace.update_info(name="New")

    def test_modify_when_archived_raises(self, archived_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceArchivedException):
            archived_workspace.update_info(name="New")

    def test_modify_when_pending_deletion_raises(self, pending_deletion_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            pending_deletion_workspace.update_info(name="New")

    def test_add_owner_when_suspended_raises(self, suspended_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            suspended_workspace.add_owner(IdFactory())

    def test_remove_owner_when_suspended_raises(self, suspended_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            suspended_workspace.remove_owner(suspended_workspace.owner_ids[0])

    def test_archive_when_suspended_raises(self, suspended_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            suspended_workspace.archive()

    def test_suspend_when_pending_deletion_raises(self, pending_deletion_workspace: Workspace) -> None:
        with pytest.raises(WorkspaceSuspendedException):
            pending_deletion_workspace.suspend("reason")


# ═══════════════════════════════════════════════════════════════════════════
# Политики
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspacePolicies:
    def test_update_security_policy(self, workspace: Workspace) -> None:
        policy = SecurityPolicy(require_2fa=True)
        workspace.update_security_policy(policy)
        assert workspace.security_policy.require_2fa is True

    def test_update_security_policy_emits_event(self, workspace: Workspace) -> None:
        policy = SecurityPolicy(require_2fa=True)
        workspace.update_security_policy(policy)
        events = workspace.clear_domain_events()
        assert any(isinstance(e, SecurityPolicyChanged) for e in events)

    def test_update_security_policy_no_change_no_event(self, workspace: Workspace) -> None:
        workspace.update_security_policy(workspace.security_policy)
        events = workspace.clear_domain_events()
        assert not any(isinstance(e, SecurityPolicyChanged) for e in events)

    def test_update_membership_policy(self, workspace: Workspace) -> None:
        policy = MembershipPolicy(require_approval=True)
        workspace.update_membership_policy(policy)
        assert workspace.membership_policy.require_approval is True

    def test_update_membership_policy_emits_event(self, workspace: Workspace) -> None:
        policy = MembershipPolicy(require_approval=True)
        workspace.update_membership_policy(policy)
        events = workspace.clear_domain_events()
        assert any(isinstance(e, MembershipPolicyChanged) for e in events)

    def test_update_limits(self, workspace: Workspace) -> None:
        limits = WorkspaceLimits(max_members=100)
        workspace.update_limits(limits)
        assert workspace.limits.max_members == 100

    def test_update_limits_emits_event(self, workspace: Workspace) -> None:
        limits = WorkspaceLimits(max_members=100)
        workspace.update_limits(limits)
        events = workspace.clear_domain_events()
        assert any(isinstance(e, WorkspaceLimitsChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Иерархия
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWorkspaceHierarchy:
    def test_move_under_parent(self, workspace: Workspace) -> None:
        parent_id = IdFactory()
        workspace.move_under_parent(parent_id)
        assert workspace.parent_workspace_id == parent_id

    def test_move_under_parent_emits_child_created(self, workspace: Workspace) -> None:
        parent_id = IdFactory()
        workspace.move_under_parent(parent_id)
        events = workspace.clear_domain_events()
        assert any(isinstance(e, ChildWorkspaceCreated) for e in events)

    def test_detach_from_parent(self, workspace: Workspace) -> None:
        parent_id = IdFactory()
        workspace.move_under_parent(parent_id)
        workspace.clear_domain_events()
        workspace.detach_from_parent()
        assert workspace.parent_workspace_id is None
