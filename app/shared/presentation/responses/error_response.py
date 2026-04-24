from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """
    Детализация ошибки для API-ответа.

    Атрибуты:
        code: Код ошибки (например, "VALIDATION_ERROR").
        message: Человекочитаемое описание.
        field: Имя поля (для ошибок валидации).
    """

    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    """
    Стандартный ответ с ошибкой.

    Атрибуты:
        success: Всегда False.
        error: Детализация ошибки.
        details: Список дополнительных деталей (для множественных ошибок валидации).
    """

    model_config = ConfigDict(from_attributes=True)

    success: bool = False
    error: ErrorDetail
    details: list[ErrorDetail] = Field(default_factory=list)
