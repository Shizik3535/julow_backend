from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspaceQuery(BaseQuery):
    """
    Запрос workspace по ID.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: Идентификатор workspace.
    """

    caller_id: str
    workspace_id: str


class GetWorkspaceHandler(BaseQueryHandler[GetWorkspaceQuery, WorkspaceDTO]):
    """Обработчик запроса workspace по ID."""

    REQUIRED_PERMISSION = "ws.read"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceQuery) -> WorkspaceDTO:
        ws_id = Id.from_string(query.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        return WorkspaceDTO(
            id=str(ws.id),
            name=ws.name,
            status=ws.status.value,
            workspace_type=ws.workspace_type.value,
            organization_id=str(ws.organization_id) if ws.organization_id else None,
            parent_workspace_id=str(ws.parent_workspace_id) if ws.parent_workspace_id else None,
            personalization={
                "color": ws.personalization.color.value if ws.personalization.color else None,
                "icon": ws.personalization.icon if ws.personalization.icon else None,
                "display_name": ws.personalization.display_name,
                "description": ws.personalization.description,
                "branding": {
                    "logo_url": str(ws.personalization.branding.logo_url) if ws.personalization.branding and ws.personalization.branding.logo_url else None,
                    "cover_image_url": str(ws.personalization.branding.cover_image_url) if ws.personalization.branding and ws.personalization.branding.cover_image_url else None,
                    "custom_css": ws.personalization.branding.custom_css if ws.personalization.branding else None,
                } if ws.personalization.branding else None,
            },
            owner_ids=[str(oid) for oid in ws.owner_ids],
            security_policy={
                "pin_code_enabled": ws.security_policy.pin_code_enabled,
                "password_enabled": ws.security_policy.password_enabled,
                "ip_allowlist": ws.security_policy.ip_allowlist,
                "sso_mode": ws.security_policy.sso_mode.value,
                "require_2fa": ws.security_policy.require_2fa,
                "session_timeout_minutes": ws.security_policy.session_timeout_minutes,
                "inherit_from_parent": ws.security_policy.inherit_from_parent,
            },
            membership_policy={
                "allow_invitation_links": ws.membership_policy.allow_invitation_links,
                "default_role": ws.membership_policy.default_role,
                "require_approval": ws.membership_policy.require_approval,
                "max_members": ws.membership_policy.max_members,
                "allowed_email_domains": ws.membership_policy.allowed_email_domains,
                "auto_add_from_org": ws.membership_policy.auto_add_from_org,
                "inherit_from_parent": ws.membership_policy.inherit_from_parent,
            },
            limits={
                "max_projects": ws.limits.max_projects,
                "max_members": ws.limits.max_members,
                "max_storage_bytes": ws.limits.max_storage_bytes,
                "max_file_size_bytes": ws.limits.max_file_size_bytes,
                "max_teams": ws.limits.max_teams,
            },
            created_at=ws.created_at,
            updated_at=ws.updated_at,
        )
