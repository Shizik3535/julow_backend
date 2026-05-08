from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from fastapi import APIRouter, HTTPException

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions.business_rule_violation_exception import BusinessRuleViolationException
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.exceptions.validation_exception import ValidationException
from app.shared.presentation.base_presenter import BasePresenter

class BaseController(ABC):
    """
    Базовый контроллер (API Controller).

    Предоставляет общую структуру для контроллеров
    в presentation-слое каждого Bounded Context.

    Контроллер:
        - Принимает HTTP-запросы
        - Преобразует данные запроса в Command/Query
        - Передаёт в CommandHandler/QueryHandler
        - Возвращает стандартизированный ответ

    Правила:
        - Не содержит бизнес-логики
        - Зависит от application-слоя (через handlers)
        - Один контроллер = одна группа связанных endpoint'ов

    Аргументы конструктора:
        prefix: Префикс для всех маршрутов контроллера.
        tags: Теги для группировки в OpenAPI документации.
    """

    def __init__(
        self,
        prefix: str,
        tags: list[str] | None = None,
        presenter: BasePresenter | None = None,
    ) -> None:
        self._router = APIRouter(prefix=prefix, tags=tags)
        self._presenter = presenter
        self._register_routes()

    @property
    def router(self) -> APIRouter:
        """Возвращает FastAPI router контроллера."""
        return self._router

    @abstractmethod
    def _register_routes(self) -> None:
        """Зарегистрировать маршруты контроллера."""

    def _handle_domain_exception(self, exc: DomainException) -> HTTPException:
        """Преобразовать доменное исключение в HTTPException."""
        if isinstance(exc, EntityNotFoundException):
            return HTTPException(
                status_code=404,
                detail=BasePresenter.error(
                    code="NOT_FOUND",
                    message=str(exc.message),
                ),
            )
        if isinstance(exc, ValidationException):
            return HTTPException(
                status_code=422,
                detail=BasePresenter.error(
                    code="VALIDATION_ERROR",
                    message=str(exc.message),
                ),
            )
        if isinstance(exc, BusinessRuleViolationException):
            return HTTPException(
                status_code=409,
                detail=BasePresenter.error(
                    code="BUSINESS_RULE_VIOLATION",
                    message=str(exc.message),
                ),
            )

        # Catch-all for other DomainException subclasses (e.g. status-specific)
        return HTTPException(
            status_code=409,
            detail=BasePresenter.error(
                code="DOMAIN_ERROR",
                message=str(exc.message),
            ),
        )
