from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class PublicProfileDTO(BaseDTO):
    """
    DTO публичного профиля пользователя (Profile BC).

    Ограниченная проекция агрегата UserProfile для просмотра
    другими пользователями. Содержит только открытые данные,
    без приватных настроек (appearance, localization, navigation, etc.).

    Атрибуты:
        id: Идентификатор профиля.
        user_id: ID пользователя (из Identity BC).
        avatar_url: URL аватара.
        bio: О себе.
        job_title: Должность.
        social_links: Социальные ссылки.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    user_id: str
    avatar_url: str | None = None
    bio: str | None = None
    job_title: str | None = None
    social_links: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
