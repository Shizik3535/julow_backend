from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class ReactionDTO(BaseDTO):
    """
    DTO реакции (Communication BC).

    Атрибуты:
        user_id: UUID пользователя.
        emoji: Unicode emoji.
        created_at: Время создания.
    """

    user_id: str
    emoji: str
    created_at: datetime | None = None
