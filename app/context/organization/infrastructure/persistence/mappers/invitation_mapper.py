from __future__ import annotations

from app.shared.domain.value_objects.email_vo import Email
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus
from app.context.organization.domain.value_objects.invitation_token import InvitationToken
from app.context.organization.infrastructure.persistence.orm_models.invitation_orm import InvitationORM


class InvitationMapper(BaseMapper[Invitation, InvitationORM]):
    """Data Mapper: Invitation ↔ InvitationORM."""

    def to_domain(self, orm_model: InvitationORM) -> Invitation:
        # Embedded InvitationToken
        link = None
        if orm_model.link_value:
            link = InvitationToken(
                value=orm_model.link_value,
                expires_at=orm_model.link_expires_at,
                max_uses=orm_model.link_max_uses,
                used_count=orm_model.link_used_count,
            )

        return Invitation(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            email=Email(orm_model.email) if orm_model.email else None,
            link=link,
            role_id=self._map_id(orm_model.role_id),
            invited_by=self._map_id(orm_model.invited_by),
            invited_at=orm_model.invited_at,
            status=InvitationStatus(orm_model.status),
            approved_by=self._map_id(orm_model.approved_by) if orm_model.approved_by else None,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Invitation) -> InvitationORM:
        return InvitationORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            email=aggregate.email.value if aggregate.email else None,
            role_id=self._map_uuid(aggregate.role_id),
            invited_by=self._map_uuid(aggregate.invited_by),
            invited_at=aggregate.invited_at,
            status=aggregate.status.value,
            approved_by=self._map_uuid(aggregate.approved_by) if aggregate.approved_by else None,
            # InvitationToken
            link_value=aggregate.link.value if aggregate.link else None,
            link_expires_at=aggregate.link.expires_at if aggregate.link else None,
            link_max_uses=aggregate.link.max_uses if aggregate.link else None,
            link_used_count=aggregate.link.used_count if aggregate.link else 0,
            # Timestamps
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
