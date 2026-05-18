from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RedeemProjectInvitationRequest(BaseModel):
    """
    Запрос на принятие приглашения по коду/токену.

    Атрибуты:
        token: Значение токена (ссылка или код).
    """

    model_config = ConfigDict(from_attributes=True)

    token: str = Field(..., description="Токен/код приглашения", min_length=1)
