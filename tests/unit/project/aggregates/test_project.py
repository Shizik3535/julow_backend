"""Unit-тесты для агрегата Project (Project BC)."""

from datetime import date

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.project_status import ProjectStatus
from app.context.project.domain.value_objects.project_visibility import ProjectVisibility
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.methodology_capabilities import MethodologyCapabilities
from app.context.project.domain.value_objects.category import Category
from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.value_objects.custom_field_type import CustomFieldType
from app.context.project.domain.entities.milestone import Milestone
from app.context.project.domain.events.project_events import (
    ProjectCreated,
    ProjectInfoChanged,
    ProjectArchived,
    ProjectRestored,
    ProjectSuspended,
    ProjectReactivated,
    ProjectDeletionRequested,
    MethodologyChanged,
    ProjectVisibilityChanged,
    MilestoneCreated,
    MilestoneUpdated,
    MilestoneStatusChanged,
)
from app.context.project.domain.exceptions.project_exceptions import (
    CannotChangeMethodologyWithActiveSprintsException,
    ProjectSuspendedException,
    ProjectArchivedException,
)
from app.context.project.domain.exceptions.project_membership_exceptions import (
    CannotRemoveLastOwnerException,
)
from app.context.project.domain.exceptions.custom_field_exceptions import (
    DuplicateCustomFieldException,
    CustomFieldDefinitionNotFoundException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectCreation:
    def test_create_with_defaults(self, new_project: Project) -> None:
        assert new_project.name == "Test Project"
        assert new_project.workspace_id is not None
        assert len(new_project.owner_ids) == 1
        assert new_project.methodology == Methodology.KANBAN
        assert new_project.status == ProjectStatus.ACTIVE
        assert new_project.visibility == ProjectVisibility.PRIVATE

    def test_create_sets_methodology_capabilities(self, new_project: Project) -> None:
        assert new_project.methodology_capabilities == MethodologyCapabilities.for_methodology(Methodology.KANBAN)

    def test_create_emits_project_created(self, new_project: Project) -> None:
        events = new_project.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProjectCreated)
        assert events[0].name == "Test Project"
        assert events[0].methodology == Methodology.KANBAN


# ═══════════════════════════════════════════════════════════════════════════
# Обновление информации
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectUpdateInfo:
    def test_update_name(self, project: Project) -> None:
        project.update_info(name="New Name")
        assert project.name == "New Name"

    def test_update_name_emits_event(self, project: Project) -> None:
        project.update_info(name="New Name")
        events = project.clear_domain_events()
        assert any(isinstance(e, ProjectInfoChanged) for e in events)

    def test_update_name_tracks_changed_fields(self, project: Project) -> None:
        project.update_info(name="New Name")
        events = project.clear_domain_events()
        event = next(e for e in events if isinstance(e, ProjectInfoChanged))
        assert "name" in event.changed_fields

    def test_update_no_change_no_event(self, project: Project) -> None:
        project.update_info(name=project.name)
        events = project.clear_domain_events()
        assert not any(isinstance(e, ProjectInfoChanged) for e in events)

    def test_update_multiple_fields(self, project: Project) -> None:
        project.update_info(name="New", color=Color("#FF5500"), category=Category(name="Dev"))
        events = project.clear_domain_events()
        event = next(e for e in events if isinstance(e, ProjectInfoChanged))
        assert "name" in event.changed_fields
        assert "color" in event.changed_fields
        assert "category" in event.changed_fields

    def test_update_info_updates_timestamp(self, project: Project) -> None:
        before = project.updated_at
        project.update_info(name="New Name")
        assert project.updated_at >= before


# ═══════════════════════════════════════════════════════════════════════════
# Владельцы
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectOwners:
    def test_add_owner(self, project: Project) -> None:
        new_owner = IdFactory()
        project.add_owner(new_owner)
        assert new_owner in project.owner_ids

    def test_add_duplicate_owner_ignored(self, project: Project) -> None:
        owner_id = project.owner_ids[0]
        initial_count = len(project.owner_ids)
        project.add_owner(owner_id)
        assert len(project.owner_ids) == initial_count

    def test_remove_owner(self, project: Project) -> None:
        second_owner = IdFactory()
        project.add_owner(second_owner)
        project.remove_owner(second_owner)
        assert second_owner not in project.owner_ids

    def test_remove_last_owner_raises(self, project: Project) -> None:
        with pytest.raises(CannotRemoveLastOwnerException):
            project.remove_owner(project.owner_ids[0])

    def test_transfer_ownership(self, project: Project) -> None:
        from_id = project.owner_ids[0]
        to_id = IdFactory()
        project.transfer_ownership(from_id=from_id, to_id=to_id)
        assert from_id not in project.owner_ids
        assert to_id in project.owner_ids

    def test_transfer_ownership_from_not_owner_raises(self, project: Project) -> None:
        with pytest.raises(ValueError):
            project.transfer_ownership(from_id=IdFactory(), to_id=IdFactory())

    def test_transfer_ownership_to_already_owner_raises(self, project: Project) -> None:
        owner_id = project.owner_ids[0]
        with pytest.raises(ValueError):
            project.transfer_ownership(from_id=owner_id, to_id=owner_id)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectStatus:
    def test_archive(self, project: Project) -> None:
        project.archive()
        assert project.status == ProjectStatus.ARCHIVED

    def test_archive_emits_event(self, project: Project) -> None:
        project.archive()
        events = project.clear_domain_events()
        assert any(isinstance(e, ProjectArchived) for e in events)

    def test_restore(self, archived_project: Project) -> None:
        archived_project.restore()
        assert archived_project.status == ProjectStatus.ACTIVE

    def test_restore_emits_event(self, archived_project: Project) -> None:
        archived_project.restore()
        events = archived_project.clear_domain_events()
        assert any(isinstance(e, ProjectRestored) for e in events)

    def test_restore_non_archived_is_noop(self, project: Project) -> None:
        project.restore()
        events = project.clear_domain_events()
        assert not any(isinstance(e, ProjectRestored) for e in events)

    def test_suspend(self, project: Project) -> None:
        project.suspend(reason="Maintenance")
        assert project.status == ProjectStatus.SUSPENDED

    def test_suspend_emits_event(self, project: Project) -> None:
        project.suspend(reason="Maintenance")
        events = project.clear_domain_events()
        event = next(e for e in events if isinstance(e, ProjectSuspended))
        assert event.reason == "Maintenance"

    def test_suspend_already_suspended_is_noop(self, suspended_project: Project) -> None:
        suspended_project.suspend(reason="Again")
        events = suspended_project.clear_domain_events()
        assert not any(isinstance(e, ProjectSuspended) for e in events)

    def test_reactivate(self, suspended_project: Project) -> None:
        suspended_project.reactivate()
        assert suspended_project.status == ProjectStatus.ACTIVE

    def test_reactivate_emits_event(self, suspended_project: Project) -> None:
        suspended_project.reactivate()
        events = suspended_project.clear_domain_events()
        assert any(isinstance(e, ProjectReactivated) for e in events)

    def test_reactivate_non_suspended_is_noop(self, project: Project) -> None:
        project.reactivate()
        events = project.clear_domain_events()
        assert not any(isinstance(e, ProjectReactivated) for e in events)

    def test_request_deletion(self, project: Project) -> None:
        project.request_deletion()
        assert project.status == ProjectStatus.PENDING_DELETION

    def test_request_deletion_emits_event(self, project: Project) -> None:
        project.request_deletion()
        events = project.clear_domain_events()
        assert any(isinstance(e, ProjectDeletionRequested) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Инварианты
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectInvariants:
    def test_update_info_when_suspended_raises(self, suspended_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            suspended_project.update_info(name="New")

    def test_update_info_when_archived_raises(self, archived_project: Project) -> None:
        with pytest.raises(ProjectArchivedException):
            archived_project.update_info(name="New")

    def test_update_info_when_pending_deletion_raises(self, pending_deletion_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            pending_deletion_project.update_info(name="New")

    def test_add_owner_when_suspended_raises(self, suspended_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            suspended_project.add_owner(IdFactory())

    def test_archive_when_suspended_raises(self, suspended_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            suspended_project.archive()

    def test_change_methodology_when_suspended_raises(self, suspended_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            suspended_project.change_methodology(Methodology.SCRUM)

    def test_change_visibility_when_archived_raises(self, archived_project: Project) -> None:
        with pytest.raises(ProjectArchivedException):
            archived_project.change_visibility(ProjectVisibility.WORKSPACE)

    def test_add_custom_field_when_suspended_raises(self, suspended_project: Project) -> None:
        with pytest.raises(ProjectSuspendedException):
            suspended_project.add_custom_field(CustomFieldDefinition(name="x"))


# ═══════════════════════════════════════════════════════════════════════════
# Методология
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMethodology:
    def test_change_methodology(self, project: Project) -> None:
        project.change_methodology(Methodology.SCRUM)
        assert project.methodology == Methodology.SCRUM
        assert project.methodology_capabilities == MethodologyCapabilities.for_methodology(Methodology.SCRUM)

    def test_change_methodology_emits_event(self, project: Project) -> None:
        project.change_methodology(Methodology.SCRUM)
        events = project.clear_domain_events()
        event = next(e for e in events if isinstance(e, MethodologyChanged))
        assert event.old_methodology == Methodology.KANBAN
        assert event.new_methodology == Methodology.SCRUM

    def test_change_methodology_with_active_sprints_raises(self, project: Project) -> None:
        with pytest.raises(CannotChangeMethodologyWithActiveSprintsException):
            project.change_methodology(Methodology.SCRUM, has_active_sprints=True)


# ═══════════════════════════════════════════════════════════════════════════
# Видимость
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectVisibility:
    def test_change_visibility(self, project: Project) -> None:
        project.change_visibility(ProjectVisibility.WORKSPACE)
        assert project.visibility == ProjectVisibility.WORKSPACE

    def test_change_visibility_emits_event(self, project: Project) -> None:
        project.change_visibility(ProjectVisibility.WORKSPACE)
        events = project.clear_domain_events()
        event = next(e for e in events if isinstance(e, ProjectVisibilityChanged))
        assert event.new_visibility == ProjectVisibility.WORKSPACE


# ═══════════════════════════════════════════════════════════════════════════
# Кастомные поля
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectCustomFields:
    def test_add_custom_field(self, project: Project) -> None:
        field = CustomFieldDefinition(name="priority", field_type=CustomFieldType.SELECT)
        project.add_custom_field(field)
        assert len(project.custom_field_definitions) == 1

    def test_add_duplicate_custom_field_raises(self, project: Project) -> None:
        field = CustomFieldDefinition(name="priority")
        project.add_custom_field(field)
        with pytest.raises(DuplicateCustomFieldException):
            project.add_custom_field(CustomFieldDefinition(name="priority"))

    def test_update_custom_field(self, project: Project) -> None:
        field = CustomFieldDefinition(name="priority", field_type=CustomFieldType.TEXT)
        project.add_custom_field(field)
        updated = CustomFieldDefinition(name="priority", field_type=CustomFieldType.SELECT, options=["low", "high"])
        project.update_custom_field(name="priority", definition=updated)
        assert project.custom_field_definitions[0].field_type == CustomFieldType.SELECT

    def test_update_nonexistent_custom_field_raises(self, project: Project) -> None:
        with pytest.raises(CustomFieldDefinitionNotFoundException):
            project.update_custom_field(name="missing", definition=CustomFieldDefinition(name="missing"))

    def test_remove_custom_field(self, project: Project) -> None:
        project.add_custom_field(CustomFieldDefinition(name="priority"))
        project.remove_custom_field(name="priority")
        assert len(project.custom_field_definitions) == 0

    def test_remove_nonexistent_custom_field_raises(self, project: Project) -> None:
        with pytest.raises(CustomFieldDefinitionNotFoundException):
            project.remove_custom_field(name="missing")


# ═══════════════════════════════════════════════════════════════════════════
# Milestones
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProjectMilestones:
    def test_add_milestone(self, project: Project) -> None:
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        assert len(project.milestones) == 1

    def test_add_milestone_emits_event(self, project: Project) -> None:
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        events = project.clear_domain_events()
        assert any(isinstance(e, MilestoneCreated) for e in events)

    def test_update_milestone(self, project: Project) -> None:
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        project.clear_domain_events()
        project.update_milestone(milestone_id=milestone.id, name="v2.0")
        assert milestone.name == "v2.0"

    def test_update_milestone_emits_event(self, project: Project) -> None:
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        project.clear_domain_events()
        project.update_milestone(milestone_id=milestone.id, name="v2.0")
        events = project.clear_domain_events()
        assert any(isinstance(e, MilestoneUpdated) for e in events)

    def test_update_nonexistent_milestone_raises(self, project: Project) -> None:
        with pytest.raises(ValueError):
            project.update_milestone(milestone_id=Id.generate(), name="x")

    def test_change_milestone_status(self, project: Project) -> None:
        from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        project.clear_domain_events()
        project.change_milestone_status(milestone_id=milestone.id, new_status=MilestoneStatus.IN_PROGRESS)
        assert milestone.status == MilestoneStatus.IN_PROGRESS

    def test_change_milestone_status_emits_event(self, project: Project) -> None:
        from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
        milestone = Milestone(name="v1.0")
        project.add_milestone(milestone)
        project.clear_domain_events()
        project.change_milestone_status(milestone_id=milestone.id, new_status=MilestoneStatus.IN_PROGRESS)
        events = project.clear_domain_events()
        assert any(isinstance(e, MilestoneStatusChanged) for e in events)

    def test_change_milestone_status_nonexistent_raises(self, project: Project) -> None:
        from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
        with pytest.raises(ValueError):
            project.change_milestone_status(milestone_id=Id.generate(), new_status=MilestoneStatus.IN_PROGRESS)
