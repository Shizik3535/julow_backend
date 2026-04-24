"""Интеграционные тесты RoleProviderAdapter (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.dto.role_dto import RoleDTO
from app.context.identity.infrastructure.integration.outboard.role_provider_adapter import (
    RoleProviderAdapter,
)
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import (
    SqlRoleRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import (
    SqlUserRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestRoleProviderAdapter:
    """Тесты RoleProviderAdapter: get_role, get_user_roles."""

    @pytest.fixture
    def adapter(
        self, role_repo: SqlRoleRepository, user_repo: SqlUserRepository,
    ) -> RoleProviderAdapter:
        return RoleProviderAdapter(role_repo=role_repo, user_repo=user_repo)

    # -- get_role --

    async def test_get_role_returns_dto(
        self, adapter: RoleProviderAdapter, make_role,
    ) -> None:
        role = await make_role(
            name="moderator", permissions=["ban", "mute"], is_system=True,
        )
        dto = await adapter.get_role(str(role.id))

        assert dto is not None
        assert isinstance(dto, RoleDTO)
        assert dto.id == str(role.id)
        assert dto.name == "moderator"
        assert dto.permissions == ["ban", "mute"]
        assert dto.is_system is True

    async def test_get_role_returns_none_for_unknown(
        self, adapter: RoleProviderAdapter,
    ) -> None:
        result = await adapter.get_role(str(Id.generate()))
        assert result is None

    async def test_get_role_includes_description(
        self, adapter: RoleProviderAdapter, role_repo,
    ) -> None:
        from app.context.identity.domain.aggregates.role import Role

        role = Role(name="viewer", permissions=["read"], description="Read-only role")
        await role_repo.add(role)

        dto = await adapter.get_role(str(role.id))
        assert dto is not None
        assert dto.description == "Read-only role"

    # -- get_user_roles --

    async def test_get_user_roles_returns_assigned(
        self, adapter: RoleProviderAdapter, make_user, make_role, user_repo,
    ) -> None:
        user = await make_user()
        r1 = await make_role(name="admin", permissions=["all"], is_system=True)
        r2 = await make_role(name="editor", permissions=["edit"])
        user.assign_role(r1.id)
        user.assign_role(r2.id)
        user.clear_domain_events()
        await user_repo.update(user)

        dtos = await adapter.get_user_roles(str(user.id))
        assert len(dtos) == 2
        names = {d.name for d in dtos}
        assert names == {"admin", "editor"}

    async def test_get_user_roles_empty_for_no_roles(
        self, adapter: RoleProviderAdapter, make_user,
    ) -> None:
        user = await make_user()
        dtos = await adapter.get_user_roles(str(user.id))
        assert dtos == []

    async def test_get_user_roles_empty_for_unknown_user(
        self, adapter: RoleProviderAdapter,
    ) -> None:
        dtos = await adapter.get_user_roles(str(Id.generate()))
        assert dtos == []
