from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from app.shared.presentation.responses import (
    ErrorDetail,
    ErrorResponse,
    MessageData,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

TDTO = TypeVar("TDTO")


class BasePresenter(ABC, Generic[TDTO]):
    """
    Базовый Presenter (представитель).

    Presenter преобразует DTO из application-слоя
    в формат, подходящий для presentation-слоя (API response).

    Разделяет логику форматирования ответа от контроллера.
    Полезен при необходимости разных форматов ответа
    для разных клиентов (web, mobile, и т.д.).

    Параметры типа:
        TDTO: Тип DTO для преобразования.
    """

    @abstractmethod
    def present(self, dto: TDTO) -> dict[str, Any]:
        """
        Преобразовать DTO в словарь для API-ответа.

        Аргументы:
            dto: DTO из application-слоя.

        Возвращает:
            Словарь, готовый для сериализации в JSON.
        """

    def present_list(self, dtos: list[TDTO]) -> list[dict[str, Any]]:
        """
        Преобразовать список DTO в список словарей.

        По умолчанию вызывает present() для каждого элемента.

        Аргументы:
            dtos: Список DTO.

        Возвращает:
            Список словарей.
        """
        return [self.present(dto) for dto in dtos]

    @staticmethod
    def success(data: Any = None) -> SuccessResponse:
        """Успешный ответ с опциональными данными."""
        return SuccessResponse(data=data)

    @staticmethod
    def message(message: str) -> MessageResponse:
        """Ответ только с сообщением."""
        return SuccessResponse[MessageData](data=MessageData(message=message))

    @staticmethod
    def paginated(
        items: list[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> PaginatedResponse:
        """Ответ с пагинированными данными."""
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def error(
        code: str,
        message: str,
        field: str | None = None,
        details: list[ErrorDetail] | None = None,
    ) -> ErrorResponse:
        """Ответ с ошибкой."""
        return ErrorResponse(
            error=ErrorDetail(code=code, message=message, field=field),
            details=details or [],
        )
