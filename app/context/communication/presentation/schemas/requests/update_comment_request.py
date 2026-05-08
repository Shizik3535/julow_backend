from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateCommentRequest(BaseModel):
    """
    Запрос обновления комментария.

    Атрибуты:
        content: Новый текст комментария.
        content_format: Формат содержимого.
    """

    model_config = ConfigDict(from_attributes=True)

    content: str | None = Field(default=None, description="Новый текст комментария")
    content_format: str = Field(default="markdown", description="Формат содержимого")
