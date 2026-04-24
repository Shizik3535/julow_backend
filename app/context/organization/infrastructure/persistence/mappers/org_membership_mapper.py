from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.entities.org_member import OrgMember
from app.context.organization.infrastructure.persistence.orm_models.org_membership_orm import (
    OrgMemberORM,
    OrgMembershipORM,
)


class OrgMembershipMapper(BaseMapper[OrgMembership, OrgMembershipORM]):
    """Data Mapper: OrgMembership ↔ OrgMembershipORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: OrgMembershipORM) -> OrgMembership:
        members = [self._member_to_domain(m) for m in orm_model.members]

        return OrgMembership(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            members=members,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: OrgMembership) -> OrgMembershipORM:
        orm = OrgMembershipORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.members = [self._member_to_orm(m, aggregate.id) for m in aggregate.members]
        return orm

    # ------------------------------------------------------------------
    # Child mappers
    # ------------------------------------------------------------------

    def _member_to_domain(self, orm: OrgMemberORM) -> OrgMember:
        return OrgMember(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            display_name=orm.display_name,
            role_id=self._map_id(orm.role_id),
            joined_at=orm.joined_at,
            is_active=orm.is_active,
            invited_by=self._map_id(orm.invited_by) if orm.invited_by else None,
        )

    def _member_to_orm(self, member: OrgMember, membership_id: Id) -> OrgMemberORM:
        return OrgMemberORM(
            id=self._map_uuid(member.id),
            membership_id=self._map_uuid(membership_id),
            user_id=self._map_uuid(member.user_id),
            display_name=member.display_name,
            role_id=self._map_uuid(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
            invited_by=self._map_uuid(member.invited_by) if member.invited_by else None,
        )
