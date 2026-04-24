from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine

from celery import Celery

from app.core.logging import get_logger
from app.shared.application.ports.background_tasks.background_tasks_port import BackgroundTasksPort

logger = get_logger(__name__)


class CeleryBackgroundTasksAdapter(BackgroundTasksPort):
    """
    Реализация BackgroundTasksPort на основе Celery.

    Делегирует выполнение задач Celery worker'ам через send_task.
    Задачи регистрируются в Bounded Context'ах через register_task.
    Для локальной разработки без Celery — используется asyncio.create_task
    как fallback.

    Аргументы конструктора:
        celery_app: Экземпляр Celery приложения.
        use_celery: Если False, используется asyncio fallback.
    """

    def __init__(self, celery_app: Celery, use_celery: bool = True) -> None:
        self._app = celery_app
        self._use_celery = use_celery

    async def run(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if self._use_celery:
            task_name = f"background.{func.__name__}"
            self._app.send_task(task_name, args=args, kwargs=kwargs)
            logger.debug("Background task dispatched via Celery", task=task_name)
        else:
            asyncio.create_task(func(*args, **kwargs))
            logger.debug("Background task dispatched via asyncio", task=func.__name__)

    async def run_delayed(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        delay_seconds: float,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if self._use_celery:
            task_name = f"background.delayed.{func.__name__}"
            self._app.send_task(
                task_name,
                args=args,
                kwargs=kwargs,
                countdown=int(delay_seconds),
            )
            logger.debug(
                "Delayed background task dispatched via Celery",
                task=task_name,
                delay=delay_seconds,
            )
        else:
            async def _delayed() -> None:
                await asyncio.sleep(delay_seconds)
                await func(*args, **kwargs)

            asyncio.create_task(_delayed())
            logger.debug(
                "Delayed background task dispatched via asyncio",
                task=func.__name__,
                delay=delay_seconds,
            )

    def send_task(
        self,
        name: str,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        countdown: int | None = None,
        eta: Any = None,
        expires: int | None = None,
    ) -> Any:
        """
        Отправить задачу на выполнение в Celery worker.

        Аргументы:
            name: Имя зарегистрированной задачи.
            args: Позиционные аргументы задачи.
            kwargs: Именованные аргументы задачи.
            countdown: Задержка перед выполнением (секунды).
            eta: Время выполнения (datetime).
            expires: Время истечения задачи (секунды).

        Возвращает:
            AsyncResult — результат задачи.
        """
        result = self._app.send_task(
            name,
            args=args,
            kwargs=kwargs,
            countdown=countdown,
            eta=eta,
            expires=expires,
        )
        logger.debug("Sent Celery task", name=name, task_id=result.id)
        return result

    def register_task(self, name: str, func: Any) -> None:
        """
        Зарегистрировать задачу в Celery.

        Аргументы:
            name: Имя задачи.
            func: Функция-обработчик задачи.
        """
        self._app.task(name=name)(func)
        logger.debug("Registered Celery task", name=name)
