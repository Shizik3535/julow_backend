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
from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy


class UpdateWorkspaceMembershipPolicyCommand(BaseCommand):
    """
    Команда обновления политики членства workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        allow_invitation_links: Разрешить ссылки-приглашения.
        default_role: Роль по умолчанию.
        require_approval: Требовать подтверждение.
        max_members: Максимум участников (None — без лимита).
        allowed_email_domains: Разрешённые домены email.
        auto_add_from_org: Автоматически добавлять из организации.
        inherit_from_parent: Наследовать от родителя.
    """

    caller_id: str
    workspace_id: str
    allow_invitation_links: bool | None = None
    default_role: str | None = None
    require_approval: bool | None = None
    max_members: int | None = None
    allowed_email_domains: list[str] | None = None
    auto_add_from_org: bool | None = None
    inherit_from_parent: bool | None = None


class UpdateWorkspaceMembershipPolicyHandler(BaseCommandHandler[UpdateWorkspaceMembershipPolicyCommand, None]):
    """Обработчик обновления политики членства workspace."""

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

    async def handle(self, command: UpdateWorkspaceMembershipPolicyCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        current = ws.membership_policy
        policy = MembershipPolicy(
            allow_invitation_links=command.allow_invitation_links if command.allow_invitation_links is not None else current.allow_invitation_links,
            default_role=command.default_role if command.default_role is not None else current.default_role,
            require_approval=command.require_approval if command.require_approval is not None else current.require_approval,
            max_members=command.max_members if command.max_members is not None else current.max_members,
            allowed_email_domains=command.allowed_email_domains if command.allowed_email_domains is not None else current.allowed_email_domains,
            auto_add_from_org=command.auto_add_from_org if command.auto_add_from_org is not None else current.auto_add_from_org,
            inherit_from_parent=command.inherit_from_parent if command.inherit_from_parent is not None else current.inherit_from_parent,
        )

        ws.update_membership_policy(policy)
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
