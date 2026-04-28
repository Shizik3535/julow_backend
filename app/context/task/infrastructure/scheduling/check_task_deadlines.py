from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timezone

from app.context.task.application.ports.integration.inboard.reminder_window_port import ReminderWindowPort
from app.context.task.domain.events.task_events import TaskDeadlineApproaching
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.application.messaging.domain_event_bus import DomainEventBus

logger = logging.getLogger(__name__)

MAX_REMINDER_WINDOW_HOURS = 168  # 7 days — максимальное окно напоминания


async def check_task_deadlines(
    task_repo: TaskRepository,
    reminder_window_port: ReminderWindowPort,
    cache_port: CachePort,
    event_bus: DomainEventBus,
) -> None:
    """
    Celery Beat задача: проверяет задачи с приближающимся дедлайном
    и публикует событие TaskDeadlineApproaching для каждого подходящего исполнителя.

    Дедупликация через Redis-ключи: task.deadline_notified:{task_id}:{user_id}
    с TTL = reminder_window_hours.
    """
    logger.info("Checking task deadlines...")

    tasks = await task_repo.get_tasks_with_upcoming_deadline(within_hours=MAX_REMINDER_WINDOW_HOURS)
    if not tasks:
        logger.info("No tasks with upcoming deadlines found.")
        return

    now_utc = datetime.now(tz=timezone.utc)
    notified_count = 0

    for task in tasks:
        if task.due_date is None:
            continue

        due_date = task.due_date  # date object
        due_datetime = datetime(due_date.year, due_date.month, due_date.day, tzinfo=timezone.utc)

        for assignee_id in task.assignee_ids:
            user_id_str = str(assignee_id)

            # Получаем окно напоминания пользователя
            try:
                reminder_window = await reminder_window_port.get_reminder_window(user_id_str)
            except Exception:
                reminder_window = 24

            # Проверяем, попадает ли дедлайн в окно напоминания
            hours_until_deadline = (due_datetime - now_utc).total_seconds() / 3600
            if hours_until_deadline > reminder_window:
                continue

            # Дедупликация: проверяем Redis-ключ
            cache_key = f"task.deadline_notified:{task.id}:{user_id_str}"
            try:
                already_notified = await cache_port.get(cache_key)
                if already_notified:
                    continue
            except Exception:
                pass  # Если Redis недоступен — продолжаем

            # Публикуем событие
            event = TaskDeadlineApproaching(
                task_id=str(task.id),
                due_date=str(due_date),
            )
            await event_bus.publish(event)

            # Ставим Redis-ключ с TTL
            try:
                await cache_port.set(cache_key, "1", ttl=int(reminder_window * 3600))
            except Exception:
                logger.warning("Failed to set deduplication key", key=cache_key)

            notified_count += 1

    logger.info("Task deadline check complete", notified=notified_count, total_tasks=len(tasks))
