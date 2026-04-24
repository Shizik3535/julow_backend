from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.profile.application.dto.profile_dto import ProfileDTO


class ProfileListDTO(BaseDTO):
    """
    DTO списка профилей (Profile BC).

    Обёртка для пагинированного списка с total.

    Атрибуты:
        items: Список профилей.
        total: Общее количество записей.
    """

    items: list[ProfileDTO] = []
    total: int = 0
