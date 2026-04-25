"""
Cross-context: Identity → Workspace.
Тестируем IdentityUserAdapter через реальные Workspace BC репозитории.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from datetime import datetime, timezone


class _RealIdentityUserProvider(IdentityUserProvider):
    """Провайдер, использующий реальные Identity BC репозитории."""

    def __init__(self, user_repo):
        self._user_repo = user_repo

    async def get_user(self, user_id: str) -> UserDTO | None:
        from app.shared.domain.value_objects.id_vo import Id as IdVO
        user = await self._user_repo.get_by_id(IdVO.from_string(user_id))
        if user is None:
            return None
        return UserDTO(
            id=str(user.id),
            email=str(user.email),
            status=user.status.value if hasattr(user.status, "value") else str(user.status),
            role_ids=[],
            is_email_confirmed=True,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

    async def get_users(self, user_ids: list[str]) -> list[UserDTO]:
        results = []
        for uid in user_ids:
            dto = await self.get_user(uid)
            if dto:
                results.append(dto)
        return results


@pytest.mark.integration
class TestIdentityUserAdapterCrossContext:
    """Cross-context: Identity → Workspace через реальные Identity BC."""

    async def test_user_exists_with_real_identity(
        self, user_repo, make_user
    ) -> None:
        user = await make_user()
        provider = _RealIdentityUserProvider(user_repo)
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.user_exists(str(user.id))
        assert result is True

    async def test_get_user_with_real_identity(
        self, user_repo, make_user
    ) -> None:
        user = await make_user()
        provider = _RealIdentityUserProvider(user_repo)
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.get_user(str(user.id))
        assert result is not None
        assert result["id"] == str(user.id)
