from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OAuthAuthorizeResponse(BaseModel):
    """
    Ответ с URL авторизации OAuth-провайдера.

    Атрибуты:
        provider: Название OAuth-провайдера.
        authorize_url: Полный URL для редиректа пользователя на страницу авторизации провайдера.
    """

    model_config = ConfigDict(from_attributes=True)

    provider: str = Field(
        ...,
        description="Название OAuth-провайдера",
        examples=["oauth_google"],
    )
    authorize_url: str = Field(
        ...,
        description="URL для редиректа пользователя на страницу авторизации провайдера",
        examples=["https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&response_type=code&scope=..."],
    )
