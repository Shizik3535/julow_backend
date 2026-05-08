from __future__ import annotations

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Тело запроса на отправку сообщения."""

    content: str | None = Field(default=None, description="Текст сообщения")
    content_format: str = Field(default="markdown")
    thread_id: str | None = Field(
        default=None, description="UUID треда (для сообщений в треде)"
    )
    reply_to_id: str | None = Field(
        default=None, description="UUID сообщения-ответа"
    )
    message_type: str = Field(default="text", description="text/system/file/voice/...")


class UpdateMessageRequest(BaseModel):
    """Тело запроса на редактирование сообщения."""

    content: str | None = Field(default=None, description="Новый текст")
    content_format: str = Field(default="markdown")


class AddMessageReactionRequest(BaseModel):
    """Тело запроса на добавление реакции."""

    emoji: str = Field(..., description="Эмодзи реакции")
