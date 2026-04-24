from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class ProfileDTO(BaseDTO):
    """
    DTO профиля пользователя (Profile BC).

    Полная проекция агрегата UserProfile для presentation-слоя
    и других BC через integration port.

    Атрибуты:
        id: Идентификатор профиля.
        user_id: ID пользователя (из Identity BC).
        avatar_url: URL аватара.
        bio: О себе.
        job_title: Должность.
        social_links: Социальные ссылки.
        appearance: Настройки внешнего вида.
        localization: Настройки локализации.
        navigation: Настройки навигации.
        notifications: Настройки уведомлений.
        privacy: Настройки приватности.
        hotkeys: Конфигурация горячих клавиш.
        sidebar_sections: Секции sidebar.
        pinned_items: Закреплённые элементы.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    user_id: str
    avatar_url: str | None = None
    bio: str | None = None
    job_title: str | None = None
    social_links: list[dict[str, Any]] = []
    appearance: dict[str, Any] = {}
    localization: dict[str, Any] = {}
    navigation: dict[str, Any] = {}
    notifications: dict[str, Any] = {}
    privacy: dict[str, Any] = {}
    hotkeys: list[dict[str, Any]] = []
    sidebar_sections: list[dict[str, Any]] = []
    pinned_items: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
