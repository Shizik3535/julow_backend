from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PreferenceEntryResponse(BaseModel):
    """Ответ с записью настройки уведомлений."""

    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="Тип уведомления", examples=["task_assigned"])
    in_app: bool = Field(default=True, description="Включён ли in-app канал")
    email: bool = Field(default=False, description="Включён ли email канал")
    push: bool = Field(default=False, description="Включён ли push канал")


class ProjectOverrideResponse(BaseModel):
    """Ответ с переопределением настроек на уровне проекта."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str = Field(..., description="UUID проекта", examples=["550e8400-e29b-41d4-a716-446655440000"])
    preferences: list[PreferenceEntryResponse] = Field(default_factory=list, description="Настройки для проекта")


class NotificationPreferencesResponse(BaseModel):
    """Ответ с настройками уведомлений."""

    model_config = ConfigDict(from_attributes=True)

    global_preferences: list[PreferenceEntryResponse] = Field(
        default_factory=list,
        description="Глобальные настройки",
    )
    project_overrides: list[ProjectOverrideResponse] = Field(
        default_factory=list,
        description="Переопределения на уровне проектов",
    )
    reminder_window_hours: int = Field(
        default=24,
        description="Окно напоминания о дедлайне (в часах, 1–168)",
        ge=1,
        le=168,
    )
