from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateLocalizationRequest(BaseModel):
    """
    Тело запроса обновления настроек локализации.

    Атрибуты:
        language: Код языка (ISO 639-1).
        timezone: Часовой пояс (IANA).
        date_format: Паттерн формата даты.
        time_format: Формат времени (H24, H12).
        week_start_day: День начала недели (MONDAY, SUNDAY, SATURDAY).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "language": "ru",
                "timezone": "Europe/Moscow",
                "date_format": "DD.MM.YYYY",
                "time_format": "H24",
                "week_start_day": "MONDAY",
            },
        },
    )

    language: str = Field(
        default="en",
        max_length=5,
        description="Код языка (ISO 639-1)",
        examples=["en", "ru"],
    )
    timezone: str = Field(
        default="UTC",
        description="Часовой пояс (IANA)",
        examples=["Europe/Moscow"],
    )
    date_format: str = Field(
        default="YYYY-MM-DD",
        pattern=r"^[DMY]{2}[./\-][DMY]{2}[./\-][DMY]{4}$",
        description="Паттерн формата даты",
        examples=["YYYY-MM-DD", "DD.MM.YYYY"],
    )
    time_format: str = Field(
        default="H24",
        description="Формат времени (H24, H12)",
        examples=["H24"],
    )
    week_start_day: str = Field(
        default="MONDAY",
        description="День начала недели (MONDAY, SUNDAY, SATURDAY)",
        examples=["MONDAY"],
    )
