from __future__ import annotations

"""
Celery task wrappers for Task BC scheduled jobs.

These synchronous functions are registered with Celery and called by Beat.
They create their own async event loop and DI container to resolve dependencies.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


def check_task_deadlines_task() -> None:
    """
    Celery-обёртка для check_task_deadlines.

    Вызывается Celery Beat каждый час.
    Создаёт свой DI-контекст и запускает асинхронную логику.
    """
    from app.context.task.infrastructure.scheduling.check_task_deadlines import check_task_deadlines

    async def _run() -> None:
        from app.core.di.container import Container

        container = Container()
        task_repo = container.task_repo()
        reminder_window_port = container.task_reminder_window_port()
        cache_port = container.cache_port()
        event_bus = container.task_event_bus()

        await check_task_deadlines(
            task_repo=task_repo,
            reminder_window_port=reminder_window_port,
            cache_port=cache_port,
            event_bus=event_bus,
        )

    asyncio.run(_run())
