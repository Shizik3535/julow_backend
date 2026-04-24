from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class OAuthLinkDTO(BaseDTO):
    """
    DTO привязки OAuth-провайдера (Identity BC).

    Атрибуты:
        provider: Название провайдера.
        provider_user_id: ID пользователя у провайдера.
        email: Email от провайдера.
        display_name: Отображаемое имя.
        linked_at: Время привязки.
    """

    provider: str
    provider_user_id: str
    email: str | None = None
    display_name: str | None = None
    linked_at: datetime | None = None
