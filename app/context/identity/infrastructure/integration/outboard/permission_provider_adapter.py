from __future__ import annotations

from app.context.identity.application.exceptions.authorization_exceptions import (
    InsufficientPermissionsException,
)
from app.context.identity.application.ports.authorization.permission_checker_port import (
    PermissionCheckerPort,
)
from app.context.identity.application.ports.integration.outboard.identity_permission_provider import (
    IdentityPermissionProvider,
)
from app.shared.domain.value_objects.id_vo import Id


class PermissionProviderAdapter(IdentityPermissionProvider):
    """
    Реализация IdentityPermissionProvider.

    Делегирует проверку разрешений внутреннему PermissionCheckerPort,
    инкапсулируя wildcard-логику и конвертацию user_id → Id.
    """

    def __init__(self, permission_checker: PermissionCheckerPort) -> None:
        self._checker = permission_checker

    async def has_permission(self, user_id: str, permission: str) -> bool:
        return await self._checker.has_permission(Id.from_string(user_id), permission)

    async def require_permission(self, user_id: str, permission: str) -> None:
        await self._checker.require_permission(Id.from_string(user_id), permission)
