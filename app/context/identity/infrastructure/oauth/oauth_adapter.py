from __future__ import annotations

from typing import Any

import httpx

from app.core.logging import get_logger
from app.context.identity.application.ports.oauth.oauth_port import OAuthPort, OAuthUserInfo

logger = get_logger(__name__)

# Конфигурация провайдеров: token URL, user-info URL, маппинг полей
_PROVIDER_CONFIG: dict[str, dict[str, Any]] = {
    "oauth_google": {
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "id_field": "sub",
        "email_field": "email",
        "name_field": "name",
    },
    "oauth_github": {
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "id_field": "id",
        "email_field": "email",
        "name_field": "login",
    },
}


class HttpxOAuthAdapter(OAuthPort):
    """
    Реализация OAuthPort на основе httpx.

    Выполняет exchange authorization code → access token
    и получение профиля пользователя от OAuth-провайдеров.

    Аргументы конструктора:
        client_id_map: Словарь provider_name → client_id.
        client_secret_map: Словарь provider_name → client_secret.
    """

    def __init__(
        self,
        client_id_map: dict[str, str],
        client_secret_map: dict[str, str],
    ) -> None:
        self._client_ids = client_id_map
        self._client_secrets = client_secret_map

    def _get_config(self, provider: str) -> dict[str, Any]:
        config = _PROVIDER_CONFIG.get(provider)
        if config is None:
            raise ValueError(f"Неизвестный OAuth-провайдер: {provider}")
        return config

    async def exchange_code(
        self, provider: str, code: str, redirect_uri: str
    ) -> str:
        config = self._get_config(provider)
        client_id = self._client_ids.get(provider, "")
        client_secret = self._client_secrets.get(provider, "")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                config["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        access_token: str = data.get("access_token", "")
        if not access_token:
            logger.error("OAuth exchange_code failed: no access_token", provider=provider)
            raise RuntimeError(f"OAuth exchange_code: пустой access_token от {provider}")

        logger.info("OAuth code exchanged", provider=provider)
        return access_token

    async def get_user_info(self, provider: str, access_token: str) -> OAuthUserInfo:
        config = self._get_config(provider)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                config["userinfo_url"],
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        provider_user_id = str(data.get(config["id_field"], ""))
        email = data.get(config["email_field"])
        display_name = data.get(config["name_field"])

        logger.info("OAuth user_info fetched", provider=provider, provider_user_id=provider_user_id)
        return OAuthUserInfo(
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
        )
