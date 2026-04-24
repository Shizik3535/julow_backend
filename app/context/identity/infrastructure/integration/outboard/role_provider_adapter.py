from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.role_dto import RoleDTO
from app.context.identity.application.ports.integration.outboard.identity_role_provider import (
    IdentityRoleProvider,
)
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.user_repository import UserRepository


class RoleProviderAdapter(IdentityRoleProvider):
    """
    Реализация IdentityRoleProvider.

    Предоставляет данные ролей другим BC
    через синхронный DI-порт.
    """

    def __init__(
        self,
        role_repo: RoleRepository,
        user_repo: UserRepository,
    ) -> None:
        self._role_repo = role_repo
        self._user_repo = user_repo

    async def get_role(self, role_id: str) -> RoleDTO | None:
        role = await self._role_repo.get_by_id(Id.from_string(role_id))
        if role is None:
            return None
        return RoleDTO(
            id=str(role.id),
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
        )

    async def get_user_roles(self, user_id: str) -> list[RoleDTO]:
        user = await self._user_repo.get_by_id(Id.from_string(user_id))
        if user is None:
            return []
        result: list[RoleDTO] = []
        for role_id in user.role_ids:
            role = await self._role_repo.get_by_id(role_id)
            if role is not None:
                result.append(
                    RoleDTO(
                        id=str(role.id),
                        name=role.name,
                        permissions=role.permissions,
                        is_system=role.is_system,
                        description=role.description,
                    )
                )
        return result
