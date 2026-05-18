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
from app.context.organization.application.ports.integration.outboard.organization_provider import (
    OrganizationProvider,
)

logger = get_logger(__name__)


class OnOrgInvitationSentNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``InvitationSent`` из Organization BC.

    Создаёт in-app уведомление приглашённому пользователю с информацией
    об организации и `invitation_id`, по которому фронт может вызвать
    accept/decline. Если пользователь с таким email ещё не зарегистрирован,
    in-app уведомление не создаётся (для этого случая работает альтернативный
    flow через email-link).

    Поля ``data``:
        - kind: "sent" — категория для UI.
        - invitation_id: для вызова POST /invitations/{id}/accept|decline.
        - org_id, org_name: для отрисовки контекста.
        - role_id: ID роли.
        - invited_by: ID отправителя приглашения.
        - email: email-цель приглашения.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        identity_port: IdentityUserPort,
        organization_provider: OrganizationProvider,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._identity_port = identity_port
        self._organization_provider = organization_provider

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "InvitationSent":
            return

        payload = event.get("payload", {})
        invitation_id = payload.get("invitation_id", "")
        org_id = payload.get("org_id", "")
        email = (payload.get("email") or "").strip()
        role_id = payload.get("role_id", "")
        invited_by = payload.get("invited_by", "")

        if not invitation_id or not org_id or not email:
            return

        user_info = await self._identity_port.get_user_by_email(email)
        if user_info is None or not user_info.get("id"):
            logger.info(
                "OnOrgInvitationSentNotify: invitee not registered, skipping in-app",
                email=email,
                invitation_id=invitation_id,
            )
            return
        recipient_id = user_info["id"]

        org_name = ""
        try:
            org_dto = await self._organization_provider.get_organization(org_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "OnOrgInvitationSentNotify: get_organization failed",
                error=str(exc),
            )
            org_dto = None
        if org_dto is not None:
            org_name = org_dto.name or ""

        data: dict[str, Any] = {
            "kind": "sent",
            "invitation_id": invitation_id,
            "org_id": org_id,
            "role_id": role_id,
            "email": email,
        }
        if invited_by:
            data["invited_by"] = invited_by
        if org_name:
            data["org_name"] = org_name

        body = (
            f"Вас пригласили в организацию «{org_name}»."
            if org_name
            else "Вас пригласили в организацию."
        )

        notification = Notification.create(
            recipient_id=Id.from_string(recipient_id),
            notification_type=NotificationType.ORGANIZATION_INVITATION,
            title="Приглашение в организацию",
            body=body,
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.IN_APP, ChannelType.EMAIL],
            data=data,
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
