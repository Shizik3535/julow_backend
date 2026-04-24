from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.identity.application.dto.role_dto import RoleDTO
from app.context.identity.application.dto.role_list_dto import RoleListDTO
from app.context.identity.domain.repositories.role_repository import RoleRepository


class GetRolesQuery(BaseQuery):
    """
    Запрос списка ролей.

    Атрибуты:
        system_only: Если True — только системные роли.
        offset: Смещение для пагинации.
        limit: Максимальное количество записей.
    """

    system_only: bool = False
    offset: int = 0
    limit: int = 100


class GetRolesHandler(BaseQueryHandler[GetRolesQuery, RoleListDTO]):
    """
    Обработчик запроса списка ролей.
    """

    def __init__(self, role_repo: RoleRepository) -> None:
        super().__init__()
        self._role_repo = role_repo

    async def handle(self, query: GetRolesQuery) -> RoleListDTO:
        if query.system_only:
            roles = await self._role_repo.get_system_roles()
        else:
            roles = await self._role_repo.search(
                offset=query.offset,
                limit=query.limit,
            )

        items = [
            RoleDTO(
                id=str(role.id),
                name=role.name,
                permissions=role.permissions,
                is_system=role.is_system,
                description=role.description,
            )
            for role in roles
        ]

        return RoleListDTO(items=items, total=len(items))
