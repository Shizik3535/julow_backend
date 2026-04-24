import time

from fastapi import FastAPI, Request, Response

from app.core.logging.logging_config import get_logger


def add_request_logging_middleware(app: FastAPI) -> None:
    logger = get_logger("request")

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
        )

        return response
