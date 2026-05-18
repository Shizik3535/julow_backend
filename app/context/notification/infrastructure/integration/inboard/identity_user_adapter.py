from __future__ import annotations

from typing import Any

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.notification.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)


class IdentityUserAdapter(IdentityUserPort):
    """Реализация IdentityUserPort (inboard) — делегирует в IdentityUserProvider из Identity BC."""

    def __init__(self, identity_user_provider: IdentityUserProvider) -> None:
        self._provider = identity_user_provider

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_user(user_id)
        if dto is None:
            return None
        return {
            "id": dto.id,
            "email": dto.email,
            "status": dto.status,
        }

    async def user_exists(self, user_id: str) -> bool:
        dto = await self._provider.get_user(user_id)
        return dto is not None

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        dto = await self._provider.get_user_by_email(email)
        if dto is None:
            return None
        return {
            "id": dto.id,
            "email": dto.email,
            "status": dto.status,
        }
