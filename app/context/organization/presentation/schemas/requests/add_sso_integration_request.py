from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddSSOIntegrationRequest(BaseModel):
    """
    Тело запроса добавления SSO-интеграции.

    Атрибуты:
        provider: Провайдер SSO.
        entity_id: Entity ID.
        sso_url: SSO URL.
        certificate: Сертификат (открытый текст).
        group_mapping: Маппинг групп IdP на роли.
        attribute_mapping: Маппинг атрибутов SSO на поля профиля.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "SAML",
                "entity_id": "https://idp.example.com/saml/metadata",
                "sso_url": "https://idp.example.com/saml/sso",
                "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                "group_mapping": {"admin_group": "admin"},
                "attribute_mapping": {"email": "mail"},
            },
        },
    )

    provider: str = Field(
        ...,
        max_length=50,
        description="Провайдер SSO",
        examples=["SAML"],
    )
    entity_id: str = Field(
        default="",
        max_length=2048,
        description="Entity ID",
        examples=["https://idp.example.com/saml/metadata"],
    )
    sso_url: str = Field(
        default="",
        max_length=2048,
        description="SSO URL",
        examples=["https://idp.example.com/saml/sso"],
    )
    certificate: str = Field(
        ...,
        description="Сертификат (открытый текст)",
    )
    group_mapping: dict[str, str] | None = Field(
        default=None,
        description="Маппинг групп IdP на роли",
    )
    attribute_mapping: dict[str, str] | None = Field(
        default=None,
        description="Маппинг атрибутов SSO на поля профиля",
    )
