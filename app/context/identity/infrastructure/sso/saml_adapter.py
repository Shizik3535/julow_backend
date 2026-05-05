from __future__ import annotations

from app.context.identity.application.ports.sso.sso_port import SSOPort, SSOUserInfo


class SamlSSOAdapter(SSOPort):
    """
    SSO-адаптер для SAML 2.0.

    Использует python3-saml для генерации AuthnRequest
    и парсинга SAMLResponse от IdP.
    """

    def build_auth_request(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        attribute_mapping: dict[str, str] | None = None,
    ) -> str:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
        from onelogin.saml2.utils import OneLogin_Saml2_Utils

        settings = self._build_settings(entity_id, sso_url, certificate, callback_url)
        auth = OneLogin_Saml2_Auth(self._prepare_request(callback_url), old_settings=settings)
        return auth.login()

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
        from onelogin.saml2.auth import OneLogin_Saml2_Auth

        settings = self._build_settings(entity_id, sso_url, certificate, callback_url)
        request_data = self._prepare_request(callback_url)
        request_data["post_data"] = response_data
        auth = OneLogin_Saml2_Auth(request_data, old_settings=settings)
        auth.process_response()

        errors = auth.get_errors()
        if errors:
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException(
                f"SAML response validation failed: {', '.join(errors)}"
            )

        if not auth.is_authenticated():
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException("SAML authentication failed")

        attributes = auth.get_attributes()
        name_id = auth.get_nameid()

        # Извлечение данных из атрибутов с учётом маппинга
        mapping = attribute_mapping or {}
        email_attr = mapping.get("email", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")
        name_attr = mapping.get("display_name", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name")
        groups_attr = mapping.get("groups", "http://schemas.xmlsoap.org/claims/Group")

        email = self._get_attribute(attributes, email_attr) or name_id
        display_name = self._get_attribute(attributes, name_attr)
        groups = attributes.get(groups_attr, [])

        return SSOUserInfo(
            provider_user_id=name_id,
            email=email,
            display_name=display_name,
            groups=groups,
            attributes={k: v[0] if v else "" for k, v in attributes.items()},
        )

    def supports_protocol(self, provider: str) -> bool:
        return provider == "saml"

    # --- Приватные методы ---

    @staticmethod
    def _get_attribute(attributes: dict, key: str) -> str | None:
        """Извлечь первое значение атрибута."""
        values = attributes.get(key, [])
        return values[0] if values else None

    @staticmethod
    def _build_settings(
        entity_id: str, sso_url: str, certificate: str, callback_url: str,
    ) -> dict:
        """Построить settings dict для python3-saml."""
        return {
            "strict": True,
            "debug": False,
            "sp": {
                "entityId": callback_url.rsplit("/callback", 1)[0],
                "assertionConsumerService": {
                    "url": callback_url,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            },
            "idp": {
                "entityId": entity_id,
                "singleSignOnService": {
                    "url": sso_url,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "x509cert": certificate,
            },
        }

    @staticmethod
    def _prepare_request(callback_url: str) -> dict:
        """Подготовить request dict для python3-saml."""
        from urllib.parse import urlparse
        parsed = urlparse(callback_url)
        return {
            "https": "on" if parsed.scheme == "https" else "off",
            "http_host": parsed.hostname or "",
            "script_name": parsed.path,
            "server_port": str(parsed.port or (443 if parsed.scheme == "https" else 80)),
            "post_data": {},
            "get_data": {},
        }
