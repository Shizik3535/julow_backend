from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SSOIntegrationResponse(BaseModel):
    """
    Ответ с данными SSO-интеграции.

    Атрибуты:
        id: UUID интеграции.
        org_id: UUID организации.
        provider: Провайдер SSO.
        entity_id: Entity ID.
        sso_url: SSO URL.
        is_active: Активна ли интеграция.
        group_mapping: Маппинг групп IdP на роли.
        attribute_mapping: Маппинг атрибутов SSO на поля профиля.
        added_at: Время добавления.
        added_by: UUID добавившего.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID интеграции",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        ...,
        description="UUID организации",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    provider: str = Field(
        ...,
        description="Провайдер SSO",
        examples=["SAML"],
    )
    entity_id: str = Field(
        default="",
        description="Entity ID",
        examples=["https://idp.example.com/saml/metadata"],
    )
    sso_url: str = Field(
        default="",
        description="SSO URL",
        examples=["https://idp.example.com/saml/sso"],
    )
    is_active: bool = Field(default=True, description="Активна ли интеграция")
    group_mapping: dict[str, str] | None = Field(
        default=None,
        description="Маппинг групп IdP на роли",
    )
    attribute_mapping: dict[str, str] | None = Field(
        default=None,
        description="Маппинг атрибутов SSO на поля профиля",
    )
    added_at: datetime = Field(..., description="Время добавления (UTC)")
    added_by: str = Field(
        default="",
        description="UUID добавившего",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
