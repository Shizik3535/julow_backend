from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.logging import get_logger
from app.shared.application.ports.notification.email_dto import EmailMessage
from app.shared.application.ports.notification.email_port import EmailPort
from app.shared.application.ports.notification.push_dto import PushMessage
from app.shared.application.ports.notification.push_port import PushPort
from app.shared.application.ports.notification.websocket_dto import WebSocketMessage
from app.shared.application.ports.notification.websocket_port import WebSocketPort
from app.context.notification.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.notification.application.ports.integration.outboard.notification_preferences_provider import (
    NotificationPreferencesProvider,
)
from app.context.notification.application.ports.notification.notification_sender_port import (
    NotificationSenderPort,
)
from app.context.notification.domain.value_objects.channel_type import ChannelType

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

logger = get_logger(__name__)


class NotificationSenderAdapter(NotificationSenderPort):
    """
    Реализация NotificationSenderPort.

    Оркестрирует отправку уведомлений по каналам:
    - IN_APP → WebSocketPort
    - EMAIL → EmailPort
    - PUSH → PushPort

    Проверяет NotificationPreferencesProvider (should_deliver + DND) перед отправкой.
    """

    def __init__(
        self,
        websocket_port: WebSocketPort,
        email_port: EmailPort,
        push_port: PushPort,
        preferences_provider: NotificationPreferencesProvider,
        identity_user_port: IdentityUserPort,
        templates_dir: Path | None = None,
    ) -> None:
        self._websocket_port = websocket_port
        self._email_port = email_port
        self._push_port = push_port
        self._preferences_provider = preferences_provider
        self._identity_user_port = identity_user_port
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir or _TEMPLATES_DIR)),
            autoescape=True,
        )

    async def send_notification(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: dict,
        channels: list[str],
        priority: str = "normal",
    ) -> None:
        # Проверка DND
        is_dnd = await self._preferences_provider.is_dnd_active(recipient_id)

        # Фильтрация каналов по настройкам и DND
        filtered_channels: list[str] = []
        for ch in channels:
            ct = ChannelType(ch)

            # DND блокирует push и email
            if is_dnd and ct in (ChannelType.PUSH, ChannelType.EMAIL):
                continue

            if not await self._preferences_provider.should_deliver(recipient_id, notification_type, ch):
                continue

            filtered_channels.append(ch)

        if not filtered_channels:
            logger.debug("Notification filtered out by preferences", recipient_id=recipient_id, notification_type=notification_type)
            return

        # Отправка по каналам
        for ch in filtered_channels:
            try:
                if ch == ChannelType.IN_APP.value:
                    await self._send_in_app(recipient_id, notification_type, title, body, data)
                elif ch == ChannelType.EMAIL.value:
                    await self._send_email(recipient_id, notification_type, title, body, data)
                elif ch == ChannelType.PUSH.value:
                    await self._send_push(recipient_id, title, body, data)
                else:
                    logger.warning("Unknown notification channel", channel=ch)
            except Exception as e:
                logger.error(
                    "Failed to send notification via channel",
                    channel=ch,
                    recipient_id=recipient_id,
                    error=str(e),
                )

    async def _send_in_app(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: dict,
    ) -> None:
        message = WebSocketMessage(
            event_type="notification.created",
            payload={
                "notification_type": notification_type,
                "title": title,
                "body": body,
                **data,
            },
        )
        await self._websocket_port.send_to_user(recipient_id, message)

    def _render_email(
        self,
        notification_type: str,
        title: str,
        body: str,
        data: dict[str, Any],
    ) -> tuple[str, str]:
        """Рендерит пару (plain_text, html) из Jinja2-шаблонов."""
        ctx: dict[str, Any] = {
            "title": title,
            "body": body,
            "year": datetime.now(tz=timezone.utc).year,
            **data,
        }

        # Пытаемся найти шаблон по notification_type, fallback на generic
        txt_name = f"{notification_type}.txt"
        html_name = f"{notification_type}.html"

        try:
            txt_tmpl = self._env.get_template(txt_name)
        except TemplateNotFound:
            txt_tmpl = self._env.get_template("generic.txt")

        try:
            html_tmpl = self._env.get_template(html_name)
        except TemplateNotFound:
            html_tmpl = self._env.get_template("generic.html")

        return txt_tmpl.render(**ctx), html_tmpl.render(**ctx)

    async def _send_email(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: dict,
    ) -> None:
        user_data = await self._identity_user_port.get_user(recipient_id)
        if user_data is None:
            logger.warning("User not found for email notification", recipient_id=recipient_id)
            return

        # TODO: Заменить dict-доступ на типизированный DTO (IdentityUserPort возвращает dict[str, Any])
        email = user_data.get("email")
        if not email:
            logger.warning("User has no email", recipient_id=recipient_id)
            return

        plain_body, html_body = self._render_email(notification_type, title, body, data)

        email_message = EmailMessage(
            to=(email,),
            subject=title,
            body=plain_body,
            html_body=html_body,
        )
        await self._email_port.send(email_message)

    async def _send_push(
        self,
        recipient_id: str,
        title: str,
        body: str,
        data: dict,
    ) -> None:
        try:
            recipient_uuid = uuid.UUID(recipient_id)
        except ValueError:
            logger.error("Invalid UUID for push recipient, skipping", recipient_id=recipient_id)
            return

        push_message = PushMessage(
            recipient_id=recipient_uuid,
            title=title,
            body=body,
            data=data,
        )
        await self._push_port.send(push_message)
