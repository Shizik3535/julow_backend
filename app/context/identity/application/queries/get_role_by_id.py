from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.role_dto import RoleDTO
from app.context.identity.domain.exceptions.user_exceptions import RoleNotFoundException
from app.context.identity.domain.repositories.role_repository import RoleRepository


class GetRoleByIdQuery(BaseQuery):
    """
    Запрос роли по ID.

    Атрибуты:
        role_id: Идентификатор роли.
    """

    role_id: str


class GetRoleByIdHandler(BaseQueryHandler[GetRoleByIdQuery, RoleDTO]):
    """
    Обработчик запроса роли по ID.
    """

    def __init__(self, role_repo: RoleRepository) -> None:
        super().__init__()
        self._role_repo = role_repo

    async def handle(self, query: GetRoleByIdQuery) -> RoleDTO:
        role = await self._role_repo.get_by_id(Id.from_string(query.role_id))
        if role is None:
            raise RoleNotFoundException(query.role_id)

        return RoleDTO(
            id=str(role.id),
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
        )
