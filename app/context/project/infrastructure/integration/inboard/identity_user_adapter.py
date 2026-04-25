from __future__ import annotations

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.project.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)


class IdentityUserAdapter(IdentityUserPort):
    """
    Реализация IdentityUserPort для Project BC.

    Делегирует в IdentityUserProvider (outboard Identity BC).
    """

    def __init__(self, identity_user_provider: IdentityUserProvider) -> None:
        self._provider = identity_user_provider

    async def user_exists(self, user_id: str) -> bool:
        user = await self._provider.get_user(user_id=user_id)
        return user is not None

    async def get_user(self, user_id: str) -> dict | None:
        user = await self._provider.get_user(user_id=user_id)
        if user is None:
            return None
        return {"id": str(user.id), "email": user.email, "status": user.status}
