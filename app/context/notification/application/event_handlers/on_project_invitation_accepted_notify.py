"""Обработчик события ``ProjectInvitationAccepted`` (Project BC)."""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_priority import (
    NotificationPriority,
)
from app.context.notification.domain.value_objects.notification_type import (
    NotificationType,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)

logger = get_logger(__name__)


class OnProjectInvitationAcceptedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``ProjectInvitationAccepted`` из Project BC.

    Отправляет inviter'у (``invited_by``) уведомление о том, что
    приглашённый пользователь принял приглашение и вступил в проект.

    Если у приглашения есть email — пытаемся показать его в теле.
    Если приглашённый — известный user, подтянем email через identity port
    как fallback (например, для link-приглашений, где event.email пуст).
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        identity_port: IdentityUserPort,
        project_provider: ProjectProvider,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._identity_port = identity_port
        self._project_provider = project_provider

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ProjectInvitationAccepted":
            return

        payload = event.get("payload", {})
        invitation_id = payload.get("invitation_id", "")
        project_id = payload.get("project_id", "")
        user_id = payload.get("user_id", "")
        invited_by = payload.get("invited_by", "")
        email = (payload.get("email") or "").strip()

        if not invited_by or not project_id:
            # Без получателя нет смысла создавать notification.
            # Может произойти для legacy-событий до обогащения payload'а.
            return

        # Дополняем email из Identity, если в event'е его не было.
        if not email and user_id:
            try:
                user_info = await self._identity_port.get_user(user_id)
                if user_info is not None:
                    email = (user_info.get("email") or "").strip()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "OnProjectInvitationAcceptedNotify: identity lookup failed",
                    error=str(exc),
                )

        # Название проекта — для подписи «в проекте «X»».
        project_name = ""
        try:
            project_dto = await self._project_provider.get_project(project_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "OnProjectInvitationAcceptedNotify: get_project failed",
                error=str(exc),
            )
            project_dto = None
        if project_dto is not None:
            project_name = project_dto.name or ""

        who = email or "Пользователь"
        body_parts: list[str] = [f"{who} принял приглашение"]
        if project_name:
            body_parts.append(f"в проект «{project_name}»")
        body = " ".join(body_parts) + "."

        data: dict[str, Any] = {
            "kind": "accepted",
            "invitation_id": invitation_id,
            "project_id": project_id,
        }
        if project_name:
            data["project_name"] = project_name
        if user_id:
            data["joined_user_id"] = user_id
        if email:
            data["joined_email"] = email

        notification = Notification.create(
            recipient_id=Id.from_string(invited_by),
            notification_type=NotificationType.PROJECT_INVITATION,
            title="Приглашение принято",
            body=body,
            priority=NotificationPriority.LOW,
            channels=[ChannelType.IN_APP],
            data=data,
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
