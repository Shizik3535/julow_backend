from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SSOUserInfo:
    """
    Информация о пользователе, полученная от SSO-провайдера.

    Атрибуты:
        provider_user_id: Уникальный ID пользователя у провайдера.
        email: Email пользователя.
        display_name: Отображаемое имя.
        groups: Список групп пользователя у провайдера.
        attributes: Дополнительные атрибуты от провайдера.
    """

    provider_user_id: str = ""
    email: str = ""
    display_name: str | None = None
    groups: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)


class SSOPort(ABC):
    """
    BC-специфичный порт для работы с SSO-провайдерами.

    Абстрагирует генерацию SSO auth request, обработку ответа IdP
    и извлечение профиля пользователя для SAML, OIDC и LDAP.

    Реализация (адаптер) находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    def build_auth_request(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        attribute_mapping: dict[str, str] | None = None,
    ) -> str:
        """
        Сгенерировать URL/запрос для редиректа пользователя на IdP.

        Аргументы:
            provider: Тип SSO-провайдера (saml, oidc, ldap).
            entity_id: Entity ID IdP.
            sso_url: URL SSO-сервера IdP.
            certificate: Сертификат IdP.
            callback_url: URL обратного вызова (SP ACS URL).
            attribute_mapping: Маппинг атрибутов (опционально).

        Возвращает:
            URL для редиректа пользователя на IdP (SAML/OIDC)
            или маркер прямой аутентификации (LDAP).
        """

    @abstractmethod
    async def process_response(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        response_data: dict,
        attribute_mapping: dict[str, str] | None = None,
    ) -> SSOUserInfo:
        """
        Обработать ответ от IdP и извлечь информацию о пользователе.

        Аргументы:
            provider: Тип SSO-провайдера.
            entity_id: Entity ID IdP.
            sso_url: URL SSO-сервера.
            certificate: Сертификат IdP.
            callback_url: URL обратного вызова (должен совпадать).
            response_data: Данные ответа от IdP (SAMLResponse, OIDC params и т.д.).
            attribute_mapping: Маппинг атрибутов.

        Возвращает:
            SSOUserInfo с данными пользователя.

        Выбрасывает:
            SSOAuthenticationException: Ошибка аутентификации SSO.
        """

    @abstractmethod
    def supports_protocol(self, provider: str) -> bool:
        """
        Проверить, поддерживается ли указанный SSO-протокол.

        Аргументы:
            provider: Тип SSO-провайдера (saml, oidc, ldap).

        Возвращает:
            True, если протокол поддерживается.
        """
