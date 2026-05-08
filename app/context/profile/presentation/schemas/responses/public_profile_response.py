from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PublicSocialLinkResponse(BaseModel):
    """Социальная ссылка в публичном профиле."""

    model_config = ConfigDict(from_attributes=True)

    platform: str = Field(..., description="Платформа", examples=["github"])
    url: str = Field(..., description="URL", examples=["https://github.com/user"])
    display_name: str | None = Field(
        default=None,
        description="Отображаемое имя",
        examples=["My GitHub"],
    )


class PublicProfileResponse(BaseModel):
    """
    Ответ с публичными данными профиля другого пользователя.

    Содержит только открытую информацию профиля,
    без приватных настроек.

    Атрибуты:
        id: UUID профиля.
        user_id: UUID пользователя (из Identity BC).
        avatar_url: URL аватара.
        bio: О себе.
        job_title: Должность.
        social_links: Социальные ссылки.
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
    social_links: list[PublicSocialLinkResponse] = Field(
        default_factory=list,
        description="Социальные ссылки пользователя",
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
