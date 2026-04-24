"""Интеграционные тесты UserProviderAdapter (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.infrastructure.integration.outboard.user_provider_adapter import (
    UserProviderAdapter,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import (
    SqlUserRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestUserProviderAdapter:
    """Тесты UserProviderAdapter: get_user, get_users."""

    @pytest.fixture
    def adapter(self, user_repo: SqlUserRepository) -> UserProviderAdapter:
        return UserProviderAdapter(user_repo=user_repo)

    # -- get_user --

    async def test_get_user_returns_dto(
        self, adapter: UserProviderAdapter, make_user,
    ) -> None:
        user = await make_user(email="provider@test.com")
        dto = await adapter.get_user(str(user.id))

        assert dto is not None
        assert isinstance(dto, UserDTO)
        assert dto.id == str(user.id)
        assert dto.email == "provider@test.com"
        assert dto.status == user.status.value
        assert dto.is_email_confirmed == user.is_email_confirmed

    async def test_get_user_returns_none_for_unknown(
        self, adapter: UserProviderAdapter,
    ) -> None:
        result = await adapter.get_user(str(Id.generate()))
        assert result is None

    async def test_get_user_includes_role_ids(
        self, adapter: UserProviderAdapter, make_user, make_role, user_repo,
    ) -> None:
        user = await make_user()
        role = await make_role(name="editor", permissions=["edit"])
        user.assign_role(role.id)
        user.clear_domain_events()
        await user_repo.update(user)

        dto = await adapter.get_user(str(user.id))
        assert dto is not None
        assert str(role.id) in dto.role_ids

    # -- get_users --

    async def test_get_users_returns_list(
        self, adapter: UserProviderAdapter, make_user,
    ) -> None:
        u1 = await make_user()
        u2 = await make_user()

        dtos = await adapter.get_users([str(u1.id), str(u2.id)])
        assert len(dtos) == 2
        returned_ids = {d.id for d in dtos}
        assert str(u1.id) in returned_ids
        assert str(u2.id) in returned_ids

    async def test_get_users_skips_unknown(
        self, adapter: UserProviderAdapter, make_user,
    ) -> None:
        user = await make_user()
        dtos = await adapter.get_users([str(user.id), str(Id.generate())])
        assert len(dtos) == 1
        assert dtos[0].id == str(user.id)

    async def test_get_users_empty_list(
        self, adapter: UserProviderAdapter,
    ) -> None:
        dtos = await adapter.get_users([])
        assert dtos == []
