from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.entities.project_member import ProjectMember
from app.context.project.infrastructure.persistence.orm_models.project_membership_orm import (
    ProjectMembershipORM,
    ProjectMemberORM,
)


class ProjectMembershipMapper(BaseMapper[ProjectMembership, ProjectMembershipORM]):
    """Data Mapper: ProjectMembership ↔ ProjectMembershipORM."""

    def to_domain(self, orm_model: ProjectMembershipORM) -> ProjectMembership:
        members = [self._member_orm_to_domain(m) for m in orm_model.members]

        return ProjectMembership(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            members=members,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: ProjectMembership) -> ProjectMembershipORM:
        orm = ProjectMembershipORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.members = [self._member_to_orm(m, aggregate.id) for m in aggregate.members]
        return orm

    # --- ProjectMember helpers ---

    def _member_orm_to_domain(self, orm: ProjectMemberORM) -> ProjectMember:
        return ProjectMember(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            role_id=self._map_id(orm.role_id),
            joined_at=orm.joined_at,
            is_active=orm.is_active,
        )

    def _member_to_orm(self, member: ProjectMember, membership_id) -> ProjectMemberORM:
        return ProjectMemberORM(
            id=self._map_uuid(member.id),
            membership_id=self._map_uuid(membership_id),
            user_id=self._map_uuid(member.user_id),
            role_id=self._map_uuid(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
        )
