from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
from app.context.workspace.domain.value_objects.sso_mode import SSOMode


class UpdateWorkspaceSecurityPolicyCommand(BaseCommand):
    """
    Команда обновления политики безопасности workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        pin_code_enabled: Включить PIN-код.
        password_enabled: Включить пароль.
        ip_allowlist: Список разрешённых IP.
        sso_mode: Режим SSO (NONE, OPTIONAL, REQUIRED).
        require_2fa: Требовать 2FA.
        session_timeout_minutes: Таймаут сессии (None — без лимита).
        inherit_from_parent: Наследовать от родителя.
    """

    caller_id: str
    workspace_id: str
    pin_code_enabled: bool | None = None
    password_enabled: bool | None = None
    ip_allowlist: list[str] | None = None
    sso_mode: str | None = None
    require_2fa: bool | None = None
    session_timeout_minutes: int | None = None
    inherit_from_parent: bool | None = None


class UpdateWorkspaceSecurityPolicyHandler(BaseCommandHandler[UpdateWorkspaceSecurityPolicyCommand, None]):
    """Обработчик обновления политики безопасности workspace."""

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateWorkspaceSecurityPolicyCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        current = ws.security_policy
        policy = SecurityPolicy(
            pin_code_enabled=command.pin_code_enabled if command.pin_code_enabled is not None else current.pin_code_enabled,
            password_enabled=command.password_enabled if command.password_enabled is not None else current.password_enabled,
            ip_allowlist=command.ip_allowlist if command.ip_allowlist is not None else current.ip_allowlist,
            sso_mode=SSOMode(command.sso_mode) if command.sso_mode is not None else current.sso_mode,
            require_2fa=command.require_2fa if command.require_2fa is not None else current.require_2fa,
            session_timeout_minutes=command.session_timeout_minutes if command.session_timeout_minutes is not None else current.session_timeout_minutes,
            inherit_from_parent=command.inherit_from_parent if command.inherit_from_parent is not None else current.inherit_from_parent,
        )

        ws.update_security_policy(policy)
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
