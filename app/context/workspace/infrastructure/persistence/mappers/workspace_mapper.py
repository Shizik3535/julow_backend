from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
from app.context.workspace.domain.value_objects.sso_mode import SSOMode
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding
from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits
from app.context.workspace.domain.value_objects.workspace_personalization import WorkspacePersonalization
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.infrastructure.persistence.orm_models.workspace_orm import WorkspaceORM


class WorkspaceMapper(BaseMapper[Workspace, WorkspaceORM]):
    """Data Mapper: Workspace ↔ WorkspaceORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: WorkspaceORM) -> Workspace:
        return Workspace(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            status=WorkspaceStatus(orm_model.status),
            workspace_type=WorkspaceType(orm_model.workspace_type),
            organization_id=self._map_id(orm_model.organization_id) if orm_model.organization_id else None,
            parent_workspace_id=self._map_id(orm_model.parent_workspace_id) if orm_model.parent_workspace_id else None,
            personalization=self._personalization_to_domain(orm_model),
            owner_ids=[self._map_id(uid) for uid in (orm_model.owner_ids or [])],
            security_policy=self._security_policy_to_domain(orm_model),
            membership_policy=self._membership_policy_to_domain(orm_model),
            limits=self._limits_to_domain(orm_model),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: Workspace) -> WorkspaceORM:
        return WorkspaceORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            status=aggregate.status.value,
            workspace_type=aggregate.workspace_type.value,
            organization_id=self._map_uuid(aggregate.organization_id) if aggregate.organization_id else None,
            parent_workspace_id=self._map_uuid(aggregate.parent_workspace_id) if aggregate.parent_workspace_id else None,
            **self._personalization_to_orm_dict(aggregate.personalization),
            owner_ids=[str(self._map_uuid(uid)) for uid in aggregate.owner_ids],
            **self._security_policy_to_orm_dict(aggregate.security_policy),
            **self._membership_policy_to_orm_dict(aggregate.membership_policy),
            **self._limits_to_orm_dict(aggregate.limits),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    # ------------------------------------------------------------------
    # WorkspacePersonalization
    # ------------------------------------------------------------------

    def _personalization_to_domain(self, orm: WorkspaceORM) -> WorkspacePersonalization:
        branding = self._branding_to_domain(orm)
        return WorkspacePersonalization(
            color=Color(orm.color) if orm.color else None,
            icon=orm.icon if orm.icon else None,
            display_name=orm.display_name,
            description=orm.description,
            branding=branding,
        )

    def _personalization_to_orm_dict(self, p: WorkspacePersonalization) -> dict:
        d: dict = {
            "color": str(p.color) if p.color else None,
            "icon": p.icon if p.icon else None,
            "display_name": p.display_name,
            "description": p.description,
        }
        d.update(self._branding_to_orm_dict(p.branding))
        return d

    # ------------------------------------------------------------------
    # WorkspaceBranding
    # ------------------------------------------------------------------

    @staticmethod
    def _branding_to_domain(orm: WorkspaceORM) -> WorkspaceBranding | None:
        has_branding = orm.logo_url or orm.cover_image_url or orm.custom_css
        if not has_branding:
            return None
        return WorkspaceBranding(
            logo_url=Url(orm.logo_url) if orm.logo_url else None,
            cover_image_url=Url(orm.cover_image_url) if orm.cover_image_url else None,
            custom_css=orm.custom_css,
        )

    @staticmethod
    def _branding_to_orm_dict(b: WorkspaceBranding | None) -> dict:
        if b is None:
            return {"logo_url": None, "cover_image_url": None, "custom_css": None}
        return {
            "logo_url": str(b.logo_url) if b.logo_url else None,
            "cover_image_url": str(b.cover_image_url) if b.cover_image_url else None,
            "custom_css": b.custom_css,
        }

    # ------------------------------------------------------------------
    # SecurityPolicy
    # ------------------------------------------------------------------

    @staticmethod
    def _security_policy_to_domain(orm: WorkspaceORM) -> SecurityPolicy:
        return SecurityPolicy(
            pin_code_enabled=orm.pin_code_enabled,
            password_enabled=orm.password_enabled,
            ip_allowlist=orm.ip_allowlist or [],
            sso_mode=SSOMode(orm.sso_mode),
            require_2fa=orm.require_2fa,
            session_timeout_minutes=orm.session_timeout_minutes,
            inherit_from_parent=orm.security_inherit_from_parent,
        )

    @staticmethod
    def _security_policy_to_orm_dict(p: SecurityPolicy) -> dict:
        return {
            "pin_code_enabled": p.pin_code_enabled,
            "password_enabled": p.password_enabled,
            "ip_allowlist": p.ip_allowlist,
            "sso_mode": p.sso_mode.value,
            "require_2fa": p.require_2fa,
            "session_timeout_minutes": p.session_timeout_minutes,
            "security_inherit_from_parent": p.inherit_from_parent,
        }

    # ------------------------------------------------------------------
    # MembershipPolicy
    # ------------------------------------------------------------------

    @staticmethod
    def _membership_policy_to_domain(orm: WorkspaceORM) -> MembershipPolicy:
        return MembershipPolicy(
            allow_invitation_links=orm.allow_invitation_links,
            default_role=orm.default_role,
            require_approval=orm.require_approval,
            max_members=orm.max_members,
            allowed_email_domains=orm.allowed_email_domains or [],
            auto_add_from_org=orm.auto_add_from_org,
            inherit_from_parent=orm.membership_inherit_from_parent,
        )

    @staticmethod
    def _membership_policy_to_orm_dict(p: MembershipPolicy) -> dict:
        return {
            "allow_invitation_links": p.allow_invitation_links,
            "default_role": p.default_role,
            "require_approval": p.require_approval,
            "max_members": p.max_members,
            "allowed_email_domains": p.allowed_email_domains,
            "auto_add_from_org": p.auto_add_from_org,
            "membership_inherit_from_parent": p.inherit_from_parent,
        }

    # ------------------------------------------------------------------
    # WorkspaceLimits
    # ------------------------------------------------------------------

    @staticmethod
    def _limits_to_domain(orm: WorkspaceORM) -> WorkspaceLimits:
        return WorkspaceLimits(
            max_projects=orm.max_projects,
            max_members=orm.ws_max_members,
            max_storage_bytes=orm.max_storage_bytes,
            max_file_size_bytes=orm.max_file_size_bytes,
            max_teams=orm.max_teams,
        )

    @staticmethod
    def _limits_to_orm_dict(l: WorkspaceLimits) -> dict:
        return {
            "max_projects": l.max_projects,
            "ws_max_members": l.max_members,
            "max_storage_bytes": l.max_storage_bytes,
            "max_file_size_bytes": l.max_file_size_bytes,
            "max_teams": l.max_teams,
        }
