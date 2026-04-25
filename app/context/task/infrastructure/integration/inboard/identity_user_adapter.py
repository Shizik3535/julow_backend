from __future__ import annotations

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.task.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)


class IdentityUserAdapter(IdentityUserPort):
    """
    Реализация inboard-порта IdentityUserPort для Task BC.

    Делегирует проверку существования пользователя в outboard-порт
    Identity BC (IdentityUserProvider).
    """

    def __init__(self, identity_user_provider: IdentityUserProvider) -> None:
        self._provider = identity_user_provider

    async def user_exists(self, user_id: str) -> bool:
        dto = await self._provider.get_user(user_id)
        return dto is not None
