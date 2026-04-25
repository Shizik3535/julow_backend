from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.project_status import ProjectStatus
from app.context.project.domain.value_objects.project_visibility import ProjectVisibility
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.methodology_capabilities import MethodologyCapabilities
from app.context.project.domain.value_objects.category import Category
from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.value_objects.custom_field_type import CustomFieldType
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
from app.context.project.domain.entities.milestone import Milestone
from app.context.project.infrastructure.persistence.orm_models.project_orm import (
    ProjectORM,
    MilestoneORM,
    ProjectCustomFieldORM,
    project_owners_table,
)


class ProjectMapper(BaseMapper[Project, ProjectORM]):
    """Data Mapper: Project ↔ ProjectORM."""

    def to_domain(self, orm_model: ProjectORM) -> Project:
        # RichText
        description = None
        if orm_model.description_raw is not None:
            fmt = RichTextFormat(orm_model.description_format) if orm_model.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=orm_model.description_raw, format=fmt)

        # Color
        color = Color(orm_model.color) if orm_model.color else None

        # Category
        category = None
        if orm_model.category_name is not None:
            cat_color = Color(orm_model.category_color) if orm_model.category_color else None
            category = Category(name=orm_model.category_name, color=cat_color)

        # Methodology + Capabilities
        methodology = Methodology(orm_model.methodology)
        capabilities = MethodologyCapabilities(
            has_sprints=orm_model.has_sprints,
            has_backlog=orm_model.has_backlog,
            has_milestones=orm_model.has_milestones,
            has_epics=orm_model.has_epics,
            has_wip_limits=orm_model.has_wip_limits,
            has_velocity=orm_model.has_velocity,
            has_retros=orm_model.has_retros,
            has_burndown=orm_model.has_burndown,
        )

        # Milestones
        milestones = [self._milestone_orm_to_domain(m) for m in orm_model.milestones]

        # Custom field definitions
        custom_fields = [self._custom_field_orm_to_domain(f) for f in orm_model.custom_field_definitions]

        return Project(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id) if orm_model.workspace_id else None,
            name=orm_model.name,
            description=description,
            icon=orm_model.icon,
            color=color,
            category=category,
            methodology=methodology,
            methodology_capabilities=capabilities,
            visibility=ProjectVisibility(orm_model.visibility),
            status=ProjectStatus(orm_model.status),
            owner_ids=[],  # заполняется отдельно через association table
            start_date=orm_model.start_date,
            deadline=orm_model.deadline,
            milestones=milestones,
            custom_field_definitions=custom_fields,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Project) -> ProjectORM:
        # RichText
        description_format = None
        description_raw = None
        if aggregate.description is not None:
            description_format = aggregate.description.format.value
            description_raw = aggregate.description.content

        # Color
        color = str(aggregate.color) if aggregate.color else None

        # Category
        category_name = aggregate.category.name if aggregate.category else None
        category_color = str(aggregate.category.color) if aggregate.category and aggregate.category.color else None

        # MethodologyCapabilities → 8 booleans
        caps = aggregate.methodology_capabilities

        orm = ProjectORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id) if aggregate.workspace_id else None,
            name=aggregate.name,
            description_format=description_format,
            description_raw=description_raw,
            icon=aggregate.icon,
            color=color,
            category_name=category_name,
            category_color=category_color,
            methodology=aggregate.methodology.value,
            has_sprints=caps.has_sprints,
            has_backlog=caps.has_backlog,
            has_milestones=caps.has_milestones,
            has_epics=caps.has_epics,
            has_wip_limits=caps.has_wip_limits,
            has_velocity=caps.has_velocity,
            has_retros=caps.has_retros,
            has_burndown=caps.has_burndown,
            visibility=aggregate.visibility.value,
            status=aggregate.status.value,
            start_date=aggregate.start_date,
            deadline=aggregate.deadline,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # Milestones
        orm.milestones = [self._milestone_to_orm(m, aggregate.id) for m in aggregate.milestones]

        # Custom field definitions
        orm.custom_field_definitions = [
            self._custom_field_to_orm(f, aggregate.id) for f in aggregate.custom_field_definitions
        ]

        return orm

    # --- Milestone helpers ---

    def _milestone_orm_to_domain(self, orm: MilestoneORM) -> Milestone:
        description = None
        if orm.description_raw is not None:
            fmt = RichTextFormat(orm.description_format) if orm.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=orm.description_raw, format=fmt)

        return Milestone(
            id=self._map_id(orm.id),
            name=orm.name,
            description=description,
            status=MilestoneStatus(orm.status),
            due_date=orm.due_date,
            completed_at=orm.completed_at,
        )

    def _milestone_to_orm(self, milestone: Milestone, project_id) -> MilestoneORM:
        description_format = None
        description_raw = None
        if milestone.description is not None:
            description_format = milestone.description.format.value
            description_raw = milestone.description.content

        return MilestoneORM(
            id=self._map_uuid(milestone.id),
            project_id=self._map_uuid(project_id),
            name=milestone.name,
            description_format=description_format,
            description_raw=description_raw,
            status=milestone.status.value,
            due_date=milestone.due_date,
            completed_at=milestone.completed_at,
        )

    # --- Custom field helpers ---

    def _custom_field_orm_to_domain(self, orm: ProjectCustomFieldORM) -> CustomFieldDefinition:
        return CustomFieldDefinition(
            name=orm.name,
            field_type=CustomFieldType(orm.field_type),
            is_required=orm.is_required,
            options=orm.options,
            default_value=orm.default_value,
            description=orm.description,
        )

    def _custom_field_to_orm(self, field: CustomFieldDefinition, project_id) -> ProjectCustomFieldORM:
        return ProjectCustomFieldORM(
            id=None,  # let DB generate
            project_id=self._map_uuid(project_id),
            name=field.name,
            field_type=field.field_type.value,
            is_required=field.is_required,
            options=field.options,
            default_value=field.default_value,
            description=field.description,
        )
