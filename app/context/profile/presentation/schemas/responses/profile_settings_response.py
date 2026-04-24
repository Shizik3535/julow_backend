from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppearanceSettingsResponse(BaseModel):
    """Настройки внешнего вида."""

    theme: str = Field(..., description="Тема оформления", examples=["dark"])
    accent_color: str = Field(..., description="Акцентный цвет (#RRGGBB)", examples=["#6366F1"])
    interface_density: str = Field(..., description="Плотность интерфейса", examples=["comfortable"])
    custom_theme: dict | None = Field(default=None, description="Пользовательская тема (если theme=custom)")


class LocalizationSettingsResponse(BaseModel):
    """Настройки локализации."""

    language: str = Field(..., description="Код языка (ISO 639-1)", examples=["en"])
    timezone: str = Field(..., description="Часовой пояс (IANA)", examples=["Europe/Moscow"])
    date_format: str = Field(..., description="Паттерн формата даты", examples=["YYYY-MM-DD"])
    time_format: str = Field(..., description="Формат времени", examples=["H24"])
    week_start_day: str = Field(..., description="День начала недели", examples=["MONDAY"])


class NavigationSettingsResponse(BaseModel):
    """Настройки навигации."""

    start_page: str = Field(..., description="Идентификатор стартовой страницы", examples=["dashboard"])


class ChannelPreferenceResponse(BaseModel):
    """Настройка канала доставки уведомления."""

    channel: str = Field(..., description="Канал доставки", examples=["email"])
    is_enabled: bool = Field(..., description="Включён ли канал")


class TypePreferenceResponse(BaseModel):
    """Настройка типа уведомления."""

    notification_type: str = Field(..., description="Тип уведомления", examples=["task_assigned"])
    is_enabled: bool = Field(..., description="Включён ли тип")
    channels: list[ChannelPreferenceResponse] = Field(default_factory=list, description="Настройки каналов")


class NotificationSettingsResponse(BaseModel):
    """Настройки уведомлений."""

    type_preferences: list[TypePreferenceResponse] = Field(
        default_factory=list, description="Настройки по типам уведомлений"
    )


class PrivacySettingsResponse(BaseModel):
    """Настройки приватности."""

    profile_visibility: str = Field(..., description="Видимость профиля", examples=["organization_only"])
    online_status_visibility: str = Field(..., description="Видимость онлайн-статуса", examples=["everyone"])
    activity_tracking_consent: str = Field(..., description="Согласие на отслеживание", examples=["granted"])


class HotkeyResponse(BaseModel):
    """Конфигурация горячей клавиши."""

    action: str = Field(..., description="Действие", examples=["SEARCH"])
    key_combination: str = Field(..., description="Комбинация клавиш", examples=["Ctrl+K"])
    is_enabled: bool = Field(..., description="Включена")


class SidebarSectionResponse(BaseModel):
    """Секция sidebar."""

    section_id: str = Field(..., description="Идентификатор секции")
    is_collapsed: bool = Field(..., description="Свернута ли секция")
    item_ids: list[str] = Field(default_factory=list, description="ID элементов")
    order: int = Field(..., description="Порядок секции")


class PinnedItemResponse(BaseModel):
    """Закреплённый элемент."""

    target_type: str = Field(..., description="Тип элемента", examples=["PROJECT"])
    target_id: str = Field(..., description="ID элемента")
    order: int = Field(..., description="Порядок")
    pinned_at: datetime = Field(..., description="Дата закрепления")


class ProfileSettingsResponse(BaseModel):
    """
    Ответ с полными настройками профиля пользователя.

    Атрибуты:
        user_id: UUID пользователя.
        appearance: Настройки внешнего вида.
        localization: Настройки локализации.
        navigation: Настройки навигации.
        notifications: Настройки уведомлений.
        privacy: Настройки приватности.
        hotkeys: Конфигурация горячих клавиш.
        sidebar_sections: Секции sidebar.
        pinned_items: Закреплённые элементы.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(
        ...,
        description="UUID пользователя",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    appearance: AppearanceSettingsResponse = Field(..., description="Настройки внешнего вида")
    localization: LocalizationSettingsResponse = Field(..., description="Настройки локализации")
    navigation: NavigationSettingsResponse = Field(..., description="Настройки навигации")
    notifications: NotificationSettingsResponse = Field(..., description="Настройки уведомлений")
    privacy: PrivacySettingsResponse = Field(..., description="Настройки приватности")
    hotkeys: list[HotkeyResponse] = Field(default_factory=list, description="Горячие клавиши")
    sidebar_sections: list[SidebarSectionResponse] = Field(
        default_factory=list, description="Секции sidebar"
    )
    pinned_items: list[PinnedItemResponse] = Field(
        default_factory=list, description="Закреплённые элементы"
    )
