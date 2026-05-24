from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileResponse(BaseModel):
    """
    Ответ с данными профиля пользователя.

    Содержит публичную информацию профиля,
    безопасную для передачи клиенту.

    Атрибуты:
        id: UUID профиля.
        user_id: UUID пользователя (из Identity BC).
        avatar_url: URL аватара.
        bio: О себе.
        job_title: Должность.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID профиля",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: str = Field(
        ...,
        description="UUID пользователя (из Identity BC)",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    display_name: str | None = Field(
        default=None,
        description="Отображаемое имя пользователя",
        examples=["Иван Петров"],
    )
    avatar_url: str | None = Field(
        default=None,
        description="URL аватара",
        examples=["https://cdn.example.com/avatars/user.png"],
    )
    bio: str | None = Field(
        default=None,
        description="О себе",
        examples=["Backend-разработчик, люблю DDD"],
    )
    job_title: str | None = Field(
        default=None,
        description="Должность",
        examples=["Senior Software Engineer"],
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
