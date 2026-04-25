from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateSSOIntegrationRequest(BaseModel):
    """
    Тело запроса обновления SSO-интеграции.

    Атрибуты:
        entity_id: Новый Entity ID.
        sso_url: Новый SSO URL.
        certificate: Новый сертификат (открытый текст).
        group_mapping: Новый маппинг групп.
        attribute_mapping: Новый маппинг атрибутов.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_id": "https://idp.example.com/saml/metadata-v2",
                "sso_url": "https://idp.example.com/saml/sso-v2",
                "certificate": None,
                "group_mapping": {"admin_group": "admin", "dev_group": "developer"},
            },
        },
    )

    entity_id: str | None = Field(default=None, max_length=2048, description="Новый Entity ID")
    sso_url: str | None = Field(default=None, max_length=2048, description="Новый SSO URL")
    certificate: str | None = Field(default=None, description="Новый сертификат (открытый текст)")
    group_mapping: dict[str, str] | None = Field(default=None, description="Новый маппинг групп")
    attribute_mapping: dict[str, str] | None = Field(default=None, description="Новый маппинг атрибутов")
