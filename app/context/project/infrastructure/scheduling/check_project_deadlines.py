from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timezone

from app.context.project.application.ports.integration.inboard.reminder_window_port import ReminderWindowPort
from app.context.project.domain.events.project_events import ProjectDeadlineApproaching
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.application.messaging.domain_event_bus import DomainEventBus

logger = logging.getLogger(__name__)

MAX_REMINDER_WINDOW_HOURS = 168  # 7 days


async def check_project_deadlines(
    project_repo: ProjectRepository,
    membership_repo: ProjectMembershipRepository,
    reminder_window_port: ReminderWindowPort,
    cache_port: CachePort,
    event_bus: DomainEventBus,
) -> None:
    """
    Celery Beat задача: проверяет проекты с приближающимся дедлайном
    и публикует событие ProjectDeadlineApproaching.

    Дедупликация через Redis-ключи: project.deadline_notified:{project_id}:{user_id}
    с TTL = reminder_window_hours.
    """
    logger.info("Checking project deadlines...")

    projects = await project_repo.get_projects_with_upcoming_deadline(within_hours=MAX_REMINDER_WINDOW_HOURS)
    if not projects:
        logger.info("No projects with upcoming deadlines found.")
        return

    now_utc = datetime.now(tz=timezone.utc)
    notified_count = 0

    for project in projects:
        if project.deadline is None:
            continue

        deadline = project.deadline
        deadline_datetime = datetime(deadline.year, deadline.month, deadline.day, tzinfo=timezone.utc)

        # Получаем участников проекта
        memberships = await membership_repo.get_members_by_project(project.id)
        member_user_ids = [str(m.user_id) for m in memberships if m.is_active]

        # Добавляем владельцев
        for owner_id in project.owner_ids:
            owner_str = str(owner_id)
            if owner_str not in member_user_ids:
                member_user_ids.append(owner_str)

        for user_id_str in member_user_ids:
            # Получаем окно напоминания пользователя
            try:
                reminder_window = await reminder_window_port.get_reminder_window(user_id_str)
            except Exception:
                reminder_window = 24

            hours_until_deadline = (deadline_datetime - now_utc).total_seconds() / 3600
            if hours_until_deadline > reminder_window:
                continue

            # Дедупликация: проверяем Redis-ключ
            cache_key = f"project.deadline_notified:{project.id}:{user_id_str}"
            try:
                already_notified = await cache_port.get(cache_key)
                if already_notified:
                    continue
            except Exception:
                pass

            # Публикуем событие
            event = ProjectDeadlineApproaching(
                project_id=str(project.id),
                deadline=str(deadline),
            )
            await event_bus.publish(event)

            # Ставим Redis-ключ с TTL
            try:
                await cache_port.set(cache_key, "1", ttl=int(reminder_window * 3600))
            except Exception:
                logger.warning("Failed to set deduplication key", key=cache_key)

            notified_count += 1

    logger.info("Project deadline check complete", notified=notified_count, total_projects=len(projects))
