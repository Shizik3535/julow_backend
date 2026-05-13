from __future__ import annotations

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.timetracking.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)


class IdentityUserAdapter(IdentityUserPort):
    """Inboard IdentityUserPort для TimeTracking BC."""

    def __init__(self, identity_user_provider: IdentityUserProvider) -> None:
        self._provider = identity_user_provider

    async def user_exists(self, user_id: str) -> bool:
        return await self._provider.user_exists(user_id)
