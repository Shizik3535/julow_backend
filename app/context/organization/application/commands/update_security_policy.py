from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy


class UpdateSecurityPolicyCommand(BaseCommand):
    """
    Команда обновления политики безопасности.

    Атрибуты:
        caller_id: ID инициатора (из JWT).
        org_id: ID организации.
        require_2fa: Требовать двухфакторную аутентификацию.
        password_min_length: Минимальная длина пароля.
        session_timeout_minutes: Таймаут сессии в минутах.
        ip_allowlist: Список разрешённых IP.
        domain_restrictions: Ограничения доменов.
        require_email_verification: Требовать подтверждение email.
    """

    caller_id: str
    org_id: str
    require_2fa: bool = False
    password_min_length: int = 8
    session_timeout_minutes: int | None = None
    ip_allowlist: list[str] = []
    domain_restrictions: list[str] = []
    require_email_verification: bool = False


class UpdateSecurityPolicyHandler(BaseCommandHandler[UpdateSecurityPolicyCommand, None]):
    """
    Обработчик обновления политики безопасности.

    Конвертирует примитивы в VO SecurityPolicy, вызывает
    доменный метод update_security_policy.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateSecurityPolicyCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        policy = SecurityPolicy(
            require_2fa=command.require_2fa,
            password_min_length=command.password_min_length,
            session_timeout_minutes=command.session_timeout_minutes,
            ip_allowlist=command.ip_allowlist,
            domain_restrictions=command.domain_restrictions,
            require_email_verification=command.require_email_verification,
        )

        org.update_security_policy(policy)
        await self._org_repo.update(org)
        await self._event_bus.publish_all(org.clear_domain_events())
