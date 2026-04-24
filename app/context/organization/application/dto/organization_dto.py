from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class OrganizationDTO(BaseDTO):
    """
    DTO организации (Organization BC).

    Полная проекция агрегата Organization для presentation-слоя
    и других BC через integration port.

    Атрибуты:
        id: Идентификатор организации.
        name: Название организации.
        status: Статус организации.
        owner_ids: Список ID владельцев.
        personalization: Настройки персонализации.
        security_policy: Политика безопасности.
        membership_policy: Политика членства.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    name: str
    status: str
    owner_ids: list[str] = []
    personalization: dict[str, Any] = {}
    security_policy: dict[str, Any] = {}
    membership_policy: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class OrganizationListDTO(BaseDTO):
    """Список организаций с общим количеством."""

    items: list[OrganizationDTO]
    total: int
