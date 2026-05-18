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
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)

logger = get_logger(__name__)


class OnWorkspaceInvitationSentNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``InvitationSent`` из Workspace BC.

    Создаёт in-app уведомление приглашённому пользователю с информацией
    о workspace и `invitation_id`, по которому фронт может вызвать
    accept/decline. Если пользователь с таким email ещё не зарегистрирован,
    in-app уведомление не создаётся (приглашение дойдёт по email-flow).

    Поля ``data``:
        - kind: "sent".
        - invitation_id: для вызова POST /invitations/{id}/accept|decline.
        - workspace_id, workspace_name: для отрисовки контекста.
        - role_id: ID роли.
        - invited_by: ID отправителя приглашения.
        - email: email-цель приглашения.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        identity_port: IdentityUserPort,
        workspace_provider: WorkspaceProvider,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._identity_port = identity_port
        self._workspace_provider = workspace_provider

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "InvitationSent":
            return

        payload = event.get("payload", {})
        invitation_id = payload.get("invitation_id", "")
        workspace_id = payload.get("workspace_id", "")
        email = (payload.get("email") or "").strip()
        role_id = payload.get("role_id", "")
        invited_by = payload.get("invited_by", "")

        if not invitation_id or not workspace_id or not email:
            return

        user_info = await self._identity_port.get_user_by_email(email)
        if user_info is None or not user_info.get("id"):
            logger.info(
                "OnWorkspaceInvitationSentNotify: invitee not registered, skipping in-app",
                email=email,
                invitation_id=invitation_id,
            )
            return
        recipient_id = user_info["id"]

        workspace_name = ""
        try:
            ws_dto = await self._workspace_provider.get_workspace(workspace_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "OnWorkspaceInvitationSentNotify: get_workspace failed",
                error=str(exc),
            )
            ws_dto = None
        if ws_dto is not None:
            workspace_name = ws_dto.name or ""

        data: dict[str, Any] = {
            "kind": "sent",
            "invitation_id": invitation_id,
            "workspace_id": workspace_id,
            "role_id": role_id,
            "email": email,
        }
        if invited_by:
            data["invited_by"] = invited_by
        if workspace_name:
            data["workspace_name"] = workspace_name

        body = (
            f"Вас пригласили в workspace «{workspace_name}»."
            if workspace_name
            else "Вас пригласили в workspace."
        )

        notification = Notification.create(
            recipient_id=Id.from_string(recipient_id),
            notification_type=NotificationType.WORKSPACE_INVITATION,
            title="Приглашение в workspace",
            body=body,
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.IN_APP, ChannelType.EMAIL],
            data=data,
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
