from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.di import Container, wire_messaging
from app.core.middleware import (
    add_correlation_id_middleware,
    add_cors_middleware,
    add_request_logging_middleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger("app.startup")
    logger.info("Starting application", app_name=settings.app.name, version=settings.app.version)

    container: Container = app.state.container

    # Start message broker
    broker = container.message_broker_port()
    await broker.start()
    logger.info("Message broker started")

    # Wire BC subscriptions to the broker (каждый BC сам знает что слушает)
    await wire_messaging(container)
    logger.info("Messaging wired")

    yield

    # Shutdown
    logger = get_logger("app.shutdown")
    await broker.stop()
    logger.info("Message broker stopped")
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """
    Создаёт и настраивает FastAPI приложение.

    Выполняет:
        1. Настройку логирования
        2. Создание DI-контейнера
        3. Настройку middleware (correlation ID, logging, CORS)
        4. Регистрацию глобальных обработчиков ошибок
        5. Подключение API роутов
    """
    setup_logging()

    container = Container()
    container.wire(modules=[])

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
        docs_url=f"{settings.app.api_prefix}/docs",
        openapi_url=f"{settings.app.api_prefix}/openapi.json",
        redoc_url=f"{settings.app.api_prefix}/redoc",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "docExpansion": "list",
            "filter": True,
            "showCommonExtensions": True,
            "displayRequestDuration": True,
        },
    )

    # Сохраняем контейнер и настройки в state приложения
    app.state.container = container
    app.state.settings = settings

    # Middleware (порядок важен — выполняются снизу вверх)
    add_correlation_id_middleware(app)
    add_request_logging_middleware(app)
    add_cors_middleware(app)

    # Глобальный обработчик ошибок
    register_exception_handlers(app)

    # API роуты
    app.include_router(api_v1_router, prefix=settings.app.api_prefix)

    return app


app = create_app()
