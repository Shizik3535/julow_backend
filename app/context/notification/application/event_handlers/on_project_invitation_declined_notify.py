"""Обработчик события ``ProjectInvitationDeclined`` (Project BC)."""

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


class OnProjectInvitationDeclinedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``ProjectInvitationDeclined`` из Project BC.

    Отправляет inviter'у уведомление: «X отклонил приглашение в проект Y».
    Не предоставляет никаких CTA — это информативное сообщение.
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
        if event.get("event_type") != "ProjectInvitationDeclined":
            return

        payload = event.get("payload", {})
        invitation_id = payload.get("invitation_id", "")
        project_id = payload.get("project_id", "")
        email = (payload.get("email") or "").strip()
        invited_by = payload.get("invited_by", "")
        user_id = payload.get("user_id", "")

        if not invited_by or not project_id:
            return

        # Fallback: подтянуть email из Identity, если приглашение было link-типа.
        if not email and user_id:
            try:
                user_info = await self._identity_port.get_user(user_id)
                if user_info is not None:
                    email = (user_info.get("email") or "").strip()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "OnProjectInvitationDeclinedNotify: identity lookup failed",
                    error=str(exc),
                )

        project_name = ""
        try:
            project_dto = await self._project_provider.get_project(project_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "OnProjectInvitationDeclinedNotify: get_project failed",
                error=str(exc),
            )
            project_dto = None
        if project_dto is not None:
            project_name = project_dto.name or ""

        who = email or "Пользователь"
        body_parts: list[str] = [f"{who} отклонил приглашение"]
        if project_name:
            body_parts.append(f"в проект «{project_name}»")
        body = " ".join(body_parts) + "."

        data: dict[str, Any] = {
            "kind": "declined",
            "invitation_id": invitation_id,
            "project_id": project_id,
        }
        if project_name:
            data["project_name"] = project_name
        if user_id:
            data["declined_user_id"] = user_id
        if email:
            data["declined_email"] = email

        notification = Notification.create(
            recipient_id=Id.from_string(invited_by),
            notification_type=NotificationType.PROJECT_INVITATION,
            title="Приглашение отклонено",
            body=body,
            priority=NotificationPriority.LOW,
            channels=[ChannelType.IN_APP],
            data=data,
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
