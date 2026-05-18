from __future__ import annotations

from app.shared.domain.value_objects.email_vo import Email
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.project.domain.aggregates.project_invitation import ProjectInvitation
from app.context.project.domain.value_objects.invitation_status import InvitationStatus
from app.context.project.domain.value_objects.invitation_token import InvitationToken
from app.context.project.infrastructure.persistence.orm_models.project_invitation_orm import (
    ProjectInvitationORM,
)


class ProjectInvitationMapper(BaseMapper[ProjectInvitation, ProjectInvitationORM]):
    """Data Mapper: ProjectInvitation ↔ ProjectInvitationORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: ProjectInvitationORM) -> ProjectInvitation:
        link = self._token_to_domain(orm_model) if orm_model.token_value else None

        return ProjectInvitation(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            workspace_id=self._map_id(orm_model.workspace_id),
            email=Email(orm_model.email) if orm_model.email else None,
            link=link,
            role_id=self._map_id(orm_model.role_id),
            invited_by=self._map_id(orm_model.invited_by),
            invited_at=orm_model.invited_at,
            status=InvitationStatus(orm_model.status),
            user_id=self._map_id(orm_model.user_id) if orm_model.user_id else None,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: ProjectInvitation) -> ProjectInvitationORM:
        token_dict = self._token_to_orm_dict(aggregate.link)

        return ProjectInvitationORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            email=str(aggregate.email) if aggregate.email else None,
            **token_dict,
            role_id=self._map_uuid(aggregate.role_id),
            invited_by=self._map_uuid(aggregate.invited_by),
            invited_at=aggregate.invited_at,
            status=aggregate.status.value,
            user_id=self._map_uuid(aggregate.user_id) if aggregate.user_id else None,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    # ------------------------------------------------------------------
    # InvitationToken
    # ------------------------------------------------------------------

    @staticmethod
    def _token_to_domain(orm: ProjectInvitationORM) -> InvitationToken:
        return InvitationToken(
            value=orm.token_value,
            expires_at=orm.token_expires_at,
            max_uses=orm.token_max_uses,
            used_count=orm.token_used_count,
        )

    @staticmethod
    def _token_to_orm_dict(token: InvitationToken | None) -> dict:
        if token is None:
            return {
                "token_value": None,
                "token_expires_at": None,
                "token_max_uses": None,
                "token_used_count": 0,
            }
        return {
            "token_value": token.value,
            "token_expires_at": token.expires_at,
            "token_max_uses": token.max_uses,
            "token_used_count": token.used_count,
        }
