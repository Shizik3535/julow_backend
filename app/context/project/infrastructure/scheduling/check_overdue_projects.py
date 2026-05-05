from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timezone

from app.context.project.domain.events.project_events import ProjectOverdue
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.application.messaging.domain_event_bus import DomainEventBus

logger = logging.getLogger(__name__)

OVERDUE_NOTIFICATION_TTL_HOURS = 24  # повторное уведомление раз в сутки


async def check_overdue_projects(
    project_repo: ProjectRepository,
    membership_repo: ProjectMembershipRepository,
    cache_port: CachePort,
    event_bus: DomainEventBus,
) -> None:
    """
    Celery Beat задача: проверяет просроченные проекты
    и публикует событие ProjectOverdue для каждого участника.

    Дедупликация через Redis-ключи: project.overdue_notified:{project_id}:{user_id}
    с TTL = 24ч.
    """
    logger.info("Checking overdue projects...")

    projects = await project_repo.get_overdue_projects()
    if not projects:
        logger.info("No overdue projects found.")
        return

    notified_count = 0

    for project in projects:
        if project.deadline is None:
            continue

        deadline = project.deadline

        # Получаем участников проекта
        memberships = await membership_repo.get_members_by_project(project.id)
        member_user_ids = [str(m.user_id) for m in memberships if m.is_active]

        # Добавляем владельцев
        for owner_id in project.owner_ids:
            owner_str = str(owner_id)
            if owner_str not in member_user_ids:
                member_user_ids.append(owner_str)

        for user_id_str in member_user_ids:
            # Дедупликация: проверяем Redis-ключ
            cache_key = f"project.overdue_notified:{project.id}:{user_id_str}"
            try:
                already_notified = await cache_port.get(cache_key)
                if already_notified:
                    continue
            except Exception:
                pass  # Если Redis недоступен — продолжаем

            # Публикуем событие
            event = ProjectOverdue(
                project_id=str(project.id),
                deadline=str(deadline),
            )
            await event_bus.publish(event)

            # Ставим Redis-ключ с TTL
            try:
                await cache_port.set(cache_key, "1", ttl=OVERDUE_NOTIFICATION_TTL_HOURS * 3600)
            except Exception:
                logger.warning("Failed to set deduplication key", key=cache_key)

            notified_count += 1

    logger.info("Overdue project check complete", notified=notified_count, total_projects=len(projects))
