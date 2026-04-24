from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class DepartmentDTO(BaseDTO):
    """
    DTO подразделения (Organization BC).

    Атрибуты:
        id: Идентификатор подразделения.
        org_id: ID организации.
        name: Название подразделения.
        parent_id: ID родительского подразделения.
        lead_id: ID руководителя.
        member_ids: Список ID участников.
        is_active: Активно ли подразделение.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str
    name: str
    parent_id: str | None = None
    lead_id: str | None = None
    member_ids: list[str] = []
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class DepartmentListDTO(BaseDTO):
    """Список подразделений с общим количеством."""

    items: list[DepartmentDTO]
    total: int
