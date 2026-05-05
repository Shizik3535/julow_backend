from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class SSOConfigDTO(BaseDTO):
    """
    DTO SSO-конфигурации для межконтекстного обмена.

    Предоставляется через outboard-порт OrganizationSSOProvider.
    Потребляется Identity BC для инициации SSO-логина.

    Атрибуты:
        org_id: ID организации.
        provider: Тип SSO-провайдера (saml, oidc, ldap).
        entity_id: Entity ID (IdP identifier).
        sso_url: URL SSO-сервера.
        certificate: Сертификат (зашифрованный).
        enforce_sso: Требуется ли обязательный вход через SSO.
        auto_provision: Автоматическая регистрация новых пользователей.
        default_role_id: ID роли по умолчанию при auto-provision.
        group_mapping: Маппинг групп IdP на роли.
        attribute_mapping: Маппинг атрибутов SSO на поля профиля.
        email_domains: Домены email, привязанные к интеграции.
    """

    org_id: str
    provider: str
    entity_id: str = ""
    sso_url: str = ""
    certificate: str = ""
    enforce_sso: bool = False
    auto_provision: bool = False
    default_role_id: str | None = None
    group_mapping: dict[str, str] | None = None
    attribute_mapping: dict[str, str] | None = None
    email_domains: list[str] = []
