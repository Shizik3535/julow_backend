from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.shared.application.application_exceptions import ApplicationException
from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions.business_rule_violation_exception import BusinessRuleViolationException
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.exceptions.validation_exception import ValidationException
from app.shared.presentation.responses import ErrorDetail, ErrorResponse

logger = get_logger("exception_handlers")


def _json_response(status_code: int, response: ErrorResponse) -> JSONResponse:
    """Строит унифицированный ответ с ошибкой."""
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрирует глобальные обработчики исключений в FastAPI приложении.

    Перехватывает:
        - DomainException (и подклассы) → ErrorResponse
        - RequestValidationError → 422 с детализацией по полям
        - StarletteHTTPException → стандартный формат ошибки
        - Exception → 500 внутренняя ошибка

    Аргументы:
        app: Экземпляр FastAPI.
    """

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
        logger.warning("Entity not found: %s", exc)
        return _json_response(
            404,
            ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message=exc.message),
            ),
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
        logger.warning("Domain validation error: %s", exc)
        return _json_response(
            422,
            ErrorResponse(
                error=ErrorDetail(code="VALIDATION_ERROR", message=exc.message),
            ),
        )

    @app.exception_handler(BusinessRuleViolationException)
    async def business_rule_handler(
        request: Request, exc: BusinessRuleViolationException
    ) -> JSONResponse:
        logger.warning("Business rule violation: %s", exc)
        return _json_response(
            409,
            ErrorResponse(
                error=ErrorDetail(code="BUSINESS_RULE_VIOLATION", message=exc.message),
            ),
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        logger.warning("Domain exception: %s", exc)
        return _json_response(
            400,
            ErrorResponse(
                error=ErrorDetail(code="DOMAIN_ERROR", message=exc.message),
            ),
        )

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ) -> JSONResponse:
        logger.warning("Application exception: %s", exc)
        return _json_response(
            exc.http_status_code,
            ErrorResponse(
                error=ErrorDetail(code=exc.error_code, message=exc.message),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details: list[ErrorDetail] = []
        for error in exc.errors():
            field_path = ".".join(str(loc) for loc in error.get("loc", []))
            details.append(
                ErrorDetail(
                    code="VALIDATION_ERROR",
                    message=error.get("msg", "Validation error"),
                    field=field_path or None,
                )
            )
        return _json_response(
            422,
            ErrorResponse(
                error=ErrorDetail(
                    code="VALIDATION_ERROR",
                    message="Request validation failed",
                ),
                details=details,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _json_response(
            exc.status_code,
            ErrorResponse(
                error=ErrorDetail(
                    code="HTTP_ERROR",
                    message=str(exc.detail),
                ),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _json_response(
            500,
            ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="Внутренняя ошибка сервера",
                ),
            ),
        )
