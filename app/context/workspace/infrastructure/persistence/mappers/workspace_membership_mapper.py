from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.entities.workspace_member import WorkspaceMember
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.infrastructure.persistence.orm_models.workspace_membership_orm import (
    WorkspaceMemberORM,
    WorkspaceMembershipORM,
)


class WorkspaceMembershipMapper(BaseMapper[WorkspaceMembership, WorkspaceMembershipORM]):
    """Data Mapper: WorkspaceMembership ↔ WorkspaceMembershipORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: WorkspaceMembershipORM) -> WorkspaceMembership:
        members = [self._member_to_domain(m) for m in orm_model.members]

        return WorkspaceMembership(
            id=self._map_id(orm_model.id),
            workspace_id=self._map_id(orm_model.workspace_id),
            members=members,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: WorkspaceMembership) -> WorkspaceMembershipORM:
        orm = WorkspaceMembershipORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.members = [self._member_to_orm(m, aggregate.id) for m in aggregate.members]
        return orm

    # ------------------------------------------------------------------
    # Child mappers
    # ------------------------------------------------------------------

    def _member_to_domain(self, orm: WorkspaceMemberORM) -> WorkspaceMember:
        return WorkspaceMember(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            display_name=orm.display_name,
            role_id=self._map_id(orm.role_id),
            joined_at=orm.joined_at,
            is_active=orm.is_active,
            source=MemberSource(orm.source),
            invited_by=self._map_id(orm.invited_by) if orm.invited_by else None,
        )

    def _member_to_orm(self, member: WorkspaceMember, membership_id: Id) -> WorkspaceMemberORM:
        return WorkspaceMemberORM(
            id=self._map_uuid(member.id),
            membership_id=self._map_uuid(membership_id),
            user_id=self._map_uuid(member.user_id),
            display_name=member.display_name,
            role_id=self._map_uuid(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
            source=member.source.value,
            invited_by=self._map_uuid(member.invited_by) if member.invited_by else None,
        )
