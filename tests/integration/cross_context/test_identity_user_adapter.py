"""Интеграционные тесты IdentityUserAdapter (реальная PostgreSQL)."""

import pytest

from app.context.identity.infrastructure.integration.outboard.user_provider_adapter import (
    UserProviderAdapter,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import (
    SqlUserRepository,
)
from app.context.profile.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestIdentityUserAdapter:
    """Тесты IdentityUserAdapter: get_user, user_exists."""

    @pytest.fixture
    def adapter(self, user_repo: SqlUserRepository) -> IdentityUserAdapter:
        provider = UserProviderAdapter(user_repo=user_repo)
        return IdentityUserAdapter(identity_user_provider=provider)

    # -- get_user --

    async def test_get_user_returns_dict(
        self, adapter: IdentityUserAdapter, make_user,
    ) -> None:
        user = await make_user(email="ident@test.com")
        result = await adapter.get_user(str(user.id))

        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == str(user.id)
        assert result["email"] == "ident@test.com"
        assert result["status"] == user.status.value
        assert result["is_email_confirmed"] == user.is_email_confirmed
        assert isinstance(result["role_ids"], list)

    async def test_get_user_returns_none_for_unknown(
        self, adapter: IdentityUserAdapter,
    ) -> None:
        result = await adapter.get_user(str(Id.generate()))
        assert result is None

    async def test_get_user_contains_role_ids(
        self, adapter: IdentityUserAdapter, make_user, make_role, user_repo,
    ) -> None:
        user = await make_user()
        role = await make_role(name="support", permissions=["tickets"])
        user.assign_role(role.id)
        user.clear_domain_events()
        await user_repo.update(user)

        result = await adapter.get_user(str(user.id))
        assert result is not None
        assert str(role.id) in result["role_ids"]

    # -- user_exists --

    async def test_user_exists_true(
        self, adapter: IdentityUserAdapter, make_user,
    ) -> None:
        user = await make_user()
        assert await adapter.user_exists(str(user.id)) is True

    async def test_user_exists_false(
        self, adapter: IdentityUserAdapter,
    ) -> None:
        assert await adapter.user_exists(str(Id.generate())) is False
