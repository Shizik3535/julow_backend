from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_settings_dto import WorkspaceSettingsDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspaceSettingsQuery(BaseQuery):
    """
    Запрос настроек workspace (политики + лимиты).

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class GetWorkspaceSettingsHandler(BaseQueryHandler[GetWorkspaceSettingsQuery, WorkspaceSettingsDTO]):
    """Обработчик запроса настроек workspace."""

    REQUIRED_PERMISSION = "ws.settings.read"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceSettingsQuery) -> WorkspaceSettingsDTO:
        ws_id = Id.from_string(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(query.workspace_id)

        return WorkspaceSettingsDTO(
            workspace_id=str(ws.id),
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
        )
