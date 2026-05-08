from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddCommentRequest(BaseModel):
    """
    Запрос создания комментария.

    Атрибуты:
        target_type: Тип комментируемой сущности (task/project/epic/...).
        target_id: UUID комментируемой сущности.
        content: Текст комментария (опционально, если есть только вложения).
        content_format: Формат содержимого (markdown/wysiwyg).
        parent_comment_id: UUID родительского комментария (для ответа).
    """

    model_config = ConfigDict(from_attributes=True)

    target_type: str = Field(
        ...,
        description="Тип комментируемой сущности",
        examples=["task"],
    )
    target_id: str = Field(
        ...,
        description="UUID комментируемой сущности",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    content: str | None = Field(
        default=None,
        description="Текст комментария",
        examples=["Отличная идея!"],
    )
    content_format: str = Field(
        default="markdown",
        description="Формат содержимого",
        examples=["markdown"],
    )
    parent_comment_id: str | None = Field(
        default=None,
        description="UUID родительского комментария (для ответа)",
    )
