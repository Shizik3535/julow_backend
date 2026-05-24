from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdatePersonalInfoRequest(BaseModel):
    """
    Тело запроса обновления персональных данных профиля.

    Атрибуты:
        bio: Текст «О себе» (до 500 символов).
        job_title: Должность (до 100 символов).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "display_name": "Иван Петров",
                "bio": "Backend-разработчик, люблю DDD и чистую архитектуру",
                "job_title": "Senior Software Engineer",
            },
        },
    )

    display_name: str | None = Field(
        default=None,
        max_length=255,
        description="Отображаемое имя пользователя",
        examples=["Иван Петров"],
    )
    bio: str | None = Field(
        default=None,
        max_length=500,
        description="Текст «О себе»",
        examples=["Backend-разработчик, люблю DDD и чистую архитектуру"],
    )
    job_title: str | None = Field(
        default=None,
        max_length=100,
        description="Должность",
        examples=["Senior Software Engineer"],
    )
