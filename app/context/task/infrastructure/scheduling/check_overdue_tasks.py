from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timezone

from app.context.task.domain.events.task_events import TaskOverdue
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.application.messaging.domain_event_bus import DomainEventBus

logger = logging.getLogger(__name__)

OVERDUE_NOTIFICATION_TTL_HOURS = 24  # повторное уведомление раз в сутки


async def check_overdue_tasks(
    task_repo: TaskRepository,
    cache_port: CachePort,
    event_bus: DomainEventBus,
) -> None:
    """
    Celery Beat задача: проверяет просроченные задачи
    и публикует событие TaskOverdue для каждого исполнителя.

    Дедупликация через Redis-ключи: task.overdue_notified:{task_id}:{user_id}
    с TTL = 24ч.
    """
    logger.info("Checking overdue tasks...")

    tasks = await task_repo.get_overdue_tasks()
    if not tasks:
        logger.info("No overdue tasks found.")
        return

    notified_count = 0

    for task in tasks:
        if task.due_date is None:
            continue

        due_date = task.due_date  # date object

        for assignee_id in task.assignee_ids:
            user_id_str = str(assignee_id)

            # Дедупликация: проверяем Redis-ключ
            cache_key = f"task.overdue_notified:{task.id}:{user_id_str}"
            try:
                already_notified = await cache_port.get(cache_key)
                if already_notified:
                    continue
            except Exception:
                pass  # Если Redis недоступен — продолжаем

            # Публикуем событие
            event = TaskOverdue(
                task_id=str(task.id),
                due_date=str(due_date),
            )
            await event_bus.publish(event)

            # Ставим Redis-ключ с TTL
            try:
                await cache_port.set(cache_key, "1", ttl=OVERDUE_NOTIFICATION_TTL_HOURS * 3600)
            except Exception:
                logger.warning("Failed to set deduplication key", key=cache_key)

            notified_count += 1

    logger.info("Overdue task check complete", notified=notified_count, total_tasks=len(tasks))
