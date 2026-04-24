from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class ProfileSettingsDTO(BaseDTO):
    """
    DTO настроек профиля (Profile BC).

    Предоставляет настройки локализации, приватности и уведомлений
    другим BC через integration port.

    Атрибуты:
        user_id: ID пользователя.
        language: Код языка (ISO 639-1).
        timezone: Часовой пояс (IANA).
        date_format: Паттерн формата даты.
        time_format: Формат времени (h24 / h12).
        week_start_day: День начала недели.
        profile_visibility: Видимость профиля.
        online_status_visibility: Видимость онлайн-статуса.
        activity_tracking_consent: Согласие на отслеживание активности.
    """

    user_id: str
    language: str
    timezone: str
    date_format: str
    time_format: str
    week_start_day: str
    profile_visibility: str
    online_status_visibility: str
    activity_tracking_consent: str
