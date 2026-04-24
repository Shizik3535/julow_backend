from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.department_dto import DepartmentDTO, DepartmentListDTO
from app.context.organization.domain.repositories.department_repository import DepartmentRepository


class GetDepartmentsByOrgQuery(BaseQuery):
    """
    Запрос списка подразделений организации.

    Атрибуты:
        org_id: ID организации.
    """

    org_id: str


class GetDepartmentsByOrgHandler(BaseQueryHandler[GetDepartmentsByOrgQuery, DepartmentListDTO]):
    """Обработчик запроса списка подразделений организации."""

    def __init__(self, department_repo: DepartmentRepository) -> None:
        super().__init__()
        self._department_repo = department_repo

    async def handle(self, query: GetDepartmentsByOrgQuery) -> DepartmentListDTO:
        departments = await self._department_repo.get_by_org_id(Id.from_string(query.org_id))

        items = [
            DepartmentDTO(
                id=str(d.id),
                org_id=str(d.org_id),
                name=d.name,
                parent_id=str(d.parent_id) if d.parent_id else None,
                lead_id=str(d.lead_id) if d.lead_id else None,
                member_ids=[str(mid) for mid in d.member_ids],
                is_active=d.is_active,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in departments
        ]
        return DepartmentListDTO(items=items, total=len(items))
