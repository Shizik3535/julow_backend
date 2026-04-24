from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OAuthLinkResponse(BaseModel):
    """
    Ответ с данными привязки OAuth-провайдера.

    Атрибуты:
        provider: Название провайдера.
        provider_user_id: ID пользователя у провайдера.
        email: Email от провайдера.
        display_name: Отображаемое имя.
        linked_at: Время привязки (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    provider: str = Field(..., description="Название OAuth-провайдера", examples=["oauth_google"])
    provider_user_id: str = Field(..., description="ID пользователя у провайдера", examples=["1234567890"])
    email: str | None = Field(default=None, description="Email от провайдера", examples=["user@gmail.com"])
    display_name: str | None = Field(default=None, description="Отображаемое имя", examples=["John Doe"])
    linked_at: datetime | None = Field(default=None, description="Время привязки (UTC)")
