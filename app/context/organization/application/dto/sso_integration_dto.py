from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class SSOIntegrationDTO(BaseDTO):
    """
    DTO SSO-интеграции (Organization BC).

    Атрибуты:
        id: Идентификатор интеграции.
        org_id: ID организации.
        provider: Провайдер SSO.
        entity_id: Entity ID.
        sso_url: SSO URL.
        is_active: Активна ли интеграция.
        group_mapping: Маппинг групп IdP на роли.
        attribute_mapping: Маппинг атрибутов SSO на поля профиля.
        added_at: Время добавления.
        added_by: ID добавившего.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str
    provider: str
    entity_id: str = ""
    sso_url: str = ""
    is_active: bool = True
    group_mapping: dict[str, str] | None = None
    attribute_mapping: dict[str, str] | None = None
    added_at: datetime
    added_by: str = ""
    created_at: datetime
    updated_at: datetime


class SSOIntegrationListDTO(BaseDTO):
    """Список SSO-интеграций с общим количеством."""

    items: list[SSOIntegrationDTO]
    total: int
