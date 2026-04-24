import uuid

import structlog
from fastapi import FastAPI, Request, Response

logger = structlog.get_logger("middleware.correlation_id")

HEADER_NAME = "X-Correlation-ID"


def add_correlation_id_middleware(app: FastAPI) -> None:
    """
    Добавляет middleware для назначения correlation ID каждому запросу.

    - Если заголовок X-Correlation-ID передан клиентом — используется он
    - Иначе генерируется новый UUID4
    - ID записывается в structlog contextvars (автоподхватывается логгером)
    - ID возвращается в заголовке ответа
    """

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next) -> Response:
        correlation_id = request.headers.get(HEADER_NAME) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)
        response.headers[HEADER_NAME] = correlation_id

        return response
