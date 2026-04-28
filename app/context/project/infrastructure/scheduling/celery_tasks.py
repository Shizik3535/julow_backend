from __future__ import annotations

"""
Celery task wrapper for Project BC scheduled jobs.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


def check_project_deadlines_task() -> None:
    """
    Celery-обёртка для check_project_deadlines.

    Вызывается Celery Beat каждый час со сдвигом.
    """
    from app.context.project.infrastructure.scheduling.check_project_deadlines import check_project_deadlines

    async def _run() -> None:
        from app.core.di.container import Container

        container = Container()
        project_repo = container.project_repo()
        membership_repo = container.project_membership_repo()
        reminder_window_port = container.project_reminder_window_port()
        cache_port = container.cache_port()
        event_bus = container.project_event_bus()

        await check_project_deadlines(
            project_repo=project_repo,
            membership_repo=membership_repo,
            reminder_window_port=reminder_window_port,
            cache_port=cache_port,
            event_bus=event_bus,
        )

    asyncio.run(_run())
