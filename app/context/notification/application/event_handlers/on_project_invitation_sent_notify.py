"""Обработчик события ``ProjectInvitationSent`` (Project BC)."""

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


class OnProjectInvitationSentNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``ProjectInvitationSent`` из Project BC.

    Создаёт in-app уведомление приглашённому пользователю с информацией
    о проекте и `invitation_id`, по которому фронт может вызвать
    accept/decline. Если пользователь с таким email ещё не зарегистрирован,
    уведомление не создаётся (для этого случая работает альтернативный
    flow через `/invite/<token>`-страницу + email).

    Поля `data`:
        - invitation_id: для вызова POST /project-invitations/{id}/accept|decline
        - project_id, project_name: для отрисовки контекста и навигации
        - role_id: для будущего отображения роли
        - invited_by: ID отправителя (полезно для UI и аудита)
        - email: email-цель приглашения
        - kind: "sent" — позволяет фронту отличить категорию notification'а
          в списке (sent / accepted / declined) без жёсткого парсинга title.
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
        if event.get("event_type") != "ProjectInvitationSent":
            return

        payload = event.get("payload", {})
        invitation_id = payload.get("invitation_id", "")
        project_id = payload.get("project_id", "")
        email = (payload.get("email") or "").strip()
        role_id = payload.get("role_id", "")
        invited_by = payload.get("invited_by", "")

        if not invitation_id or not project_id or not email:
            # Нечего адресовать — пропускаем (event пришёл с неполным
            # payload; защита от старых сообщений в очереди).
            return

        # 1) Найти пользователя по email. Если такого нет — приглашение
        # дойдёт по email-link flow, in-app notification не создаём.
        user_info = await self._identity_port.get_user_by_email(email)
        if user_info is None or not user_info.get("id"):
            logger.info(
                "OnProjectInvitationSentNotify: invitee not registered, skipping in-app",
                email=email,
                invitation_id=invitation_id,
            )
            return
        recipient_id = user_info["id"]

        # 2) Подтянуть название проекта для тела уведомления.
        project_name = ""
        try:
            project_dto = await self._project_provider.get_project(project_id)
        except Exception as exc:  # noqa: BLE001 — best-effort enrichment
            logger.warning(
                "OnProjectInvitationSentNotify: get_project failed",
                error=str(exc),
            )
            project_dto = None
        if project_dto is not None:
            project_name = project_dto.name or ""

        # 3) Собрать data — фронт будет читать invitation_id + project_id
        # для accept/decline и навигации.
        data: dict[str, Any] = {
            "kind": "sent",
            "invitation_id": invitation_id,
            "project_id": project_id,
            "role_id": role_id,
            "email": email,
        }
        if invited_by:
            data["invited_by"] = invited_by
        if project_name:
            data["project_name"] = project_name

        body = (
            f"Вас пригласили в проект «{project_name}»."
            if project_name
            else "Вас пригласили в проект."
        )

        notification = Notification.create(
            recipient_id=Id.from_string(recipient_id),
            notification_type=NotificationType.PROJECT_INVITATION,
            title="Приглашение в проект",
            body=body,
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.IN_APP, ChannelType.EMAIL],
            data=data,
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
