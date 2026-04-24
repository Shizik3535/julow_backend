from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.oauth_link_dto import OAuthLinkDTO


class OAuthLinkListDTO(BaseDTO):
    """
    DTO списка привязок OAuth-провайдеров (Identity BC).

    Атрибуты:
        items: Список привязок.
        total: Общее количество.
    """

    items: list[OAuthLinkDTO]
    total: int
