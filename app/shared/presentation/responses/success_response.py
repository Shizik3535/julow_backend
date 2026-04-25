from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """
    Успешный ответ API.

    Используется как обёртка для данных при успешном выполнении операции.
    Поддерживает дженерики: SuccessResponse[SomeDTO] — Swagger покажет схему SomeDTO.

    Атрибуты:
        success: Всегда True.
        data: Данные ответа (DTO, словарь и т.д.).
    """

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    success: bool = True
    data: T = Field(default=None)


class MessageData(BaseModel):
    """Данные ответа с сообщением."""

    message: str = Field(
        ...,
        description="Информационное сообщение",
        examples=["Operation completed successfully"],
    )


MessageResponse = SuccessResponse[MessageData]
