from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginOAuthRequest(BaseModel):
    """
    Тело запроса входа через OAuth-провайдер.

    Атрибуты:
        provider: Название провайдера (oauth_google, oauth_github, ...).
        authorization_code: Authorization code от провайдера.
        redirect_uri: URI перенаправления, использованный при получении кода.
        is_remember_me: Флаг «Запомнить меня» (увеличивает TTL сессии).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "oauth_google",
                "authorization_code": "4/0AfJohXn...",
                "redirect_uri": "https://app.example.com/oauth/callback",
                "is_remember_me": False,
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
    is_remember_me: bool = Field(
        default=False,
        description="Запомнить меня — увеличивает время жизни сессии до 30 дней",
    )
