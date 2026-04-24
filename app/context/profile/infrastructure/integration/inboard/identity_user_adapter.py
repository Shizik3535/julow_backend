from __future__ import annotations

from typing import Any

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.profile.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)


class IdentityUserAdapter(IdentityUserPort):
    """
    Реализация IdentityUserPort для Profile BC.

    Принимает IdentityUserProvider (ABC из Identity BC application)
    через конструктор — зависимость приходит из DI-контейнера.
    Не импортирует напрямую из Identity infrastructure.
    """

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
            "role_ids": dto.role_ids,
            "is_email_confirmed": dto.is_email_confirmed,
        }

    async def user_exists(self, user_id: str) -> bool:
        dto = await self._provider.get_user(user_id)
        return dto is not None
