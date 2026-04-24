from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.application.dto.department_dto import DepartmentDTO
from app.context.organization.domain.repositories.department_repository import DepartmentRepository


class GetDepartmentQuery(BaseQuery):
    """
    Запрос подразделения по ID.

    Атрибуты:
        department_id: Идентификатор подразделения.
    """

    department_id: str


class GetDepartmentHandler(BaseQueryHandler[GetDepartmentQuery, DepartmentDTO]):
    """Обработчик запроса подразделения по ID."""

    def __init__(self, department_repo: DepartmentRepository) -> None:
        super().__init__()
        self._department_repo = department_repo

    async def handle(self, query: GetDepartmentQuery) -> DepartmentDTO:
        department = await self._department_repo.get_by_id(Id.from_string(query.department_id))
        if department is None:
            raise EntityNotFoundException(entity_type="Department", id=query.department_id)

        return DepartmentDTO(
            id=str(department.id),
            org_id=str(department.org_id),
            name=department.name,
            parent_id=str(department.parent_id) if department.parent_id else None,
            lead_id=str(department.lead_id) if department.lead_id else None,
            member_ids=[str(mid) for mid in department.member_ids],
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )
