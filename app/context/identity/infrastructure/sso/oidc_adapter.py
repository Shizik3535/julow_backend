from __future__ import annotations

import secrets

import httpx

from app.context.identity.application.ports.sso.sso_port import SSOPort, SSOUserInfo


class OidcSSOAdapter(SSOPort):
    """
    SSO-адаптер для OpenID Connect.

    Использует httpx и authlib для OIDC Authorization Code Flow
    с динамической конфигурацией из Organization BC.
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
        # entity_id используется как client_id для OIDC
        # sso_url — authorize endpoint
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)

        params = {
            "response_type": "code",
            "client_id": entity_id,
            "redirect_uri": callback_url,
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
        }
        from urllib.parse import urlencode
        return f"{sso_url}?{urlencode(params)}"

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
        code = response_data.get("code")
        if not code:
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException("Missing authorization code in OIDC response")

        # certificate содержит client_secret для OIDC
        client_secret = certificate

        # Извлекаем token_url из attribute_mapping или конструируем из sso_url
        mapping = attribute_mapping or {}
        token_url = mapping.get("token_url", sso_url.replace("/authorize", "/token"))
        userinfo_url = mapping.get("userinfo_url", sso_url.replace("/authorize", "/userinfo"))

        # Обмен code на access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": callback_url,
                    "client_id": entity_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
            )

            if token_response.status_code != 200:
                from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
                raise SSOAuthenticationException(
                    f"OIDC token exchange failed: {token_response.status_code}"
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
                raise SSOAuthenticationException("No access_token in OIDC token response")

            # Получение userinfo
            userinfo_response = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
                raise SSOAuthenticationException(
                    f"OIDC userinfo request failed: {userinfo_response.status_code}"
                )

            userinfo = userinfo_response.json()

        # Маппинг полей
        email_field = mapping.get("email", "email")
        name_field = mapping.get("display_name", "name")
        id_field = mapping.get("id", "sub")
        groups_field = mapping.get("groups", "groups")

        return SSOUserInfo(
            provider_user_id=str(userinfo.get(id_field, "")),
            email=userinfo.get(email_field, ""),
            display_name=userinfo.get(name_field),
            groups=userinfo.get(groups_field, []),
            attributes={k: str(v) for k, v in userinfo.items() if isinstance(v, (str, int, float, bool))},
        )

    def supports_protocol(self, provider: str) -> bool:
        return provider == "oidc"
