from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LinkOAuthRequest(BaseModel):
    """
    Тело запроса привязки OAuth-провайдера к аккаунту.

    Сервер обменивает authorization code на access token через OAuthPort,
    затем получает профиль пользователя от провайдера.

    Атрибуты:
        provider: Название провайдера (oauth_google, oauth_github, ...).
        authorization_code: Authorization code от провайдера.
        redirect_uri: URI перенаправления, использованный при получении кода.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "oauth_google",
                "authorization_code": "4/0AfJohXn...",
                "redirect_uri": "https://app.example.com/oauth/callback",
            },
        },
    )

    provider: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Название OAuth-провайдера (oauth_google, oauth_github, oauth_yandex, oauth_apple)",
        examples=["oauth_google"],
    )
    authorization_code: str = Field(
        ...,
        min_length=1,
        description="Authorization code от OAuth-провайдера",
        examples=["4/0AfJohXn..."],
    )
    redirect_uri: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="URI перенаправления, использованный при получении кода",
        examples=["https://app.example.com/oauth/callback"],
    )
