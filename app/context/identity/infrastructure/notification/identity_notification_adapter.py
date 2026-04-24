from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.core.logging import get_logger
from app.shared.application.ports.notification.email_dto import EmailMessage
from app.shared.application.ports.notification.email_port import EmailPort
from app.context.identity.application.ports.notification.identity_notification_port import (
    IdentityNotificationPort,
)

logger = get_logger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class IdentityNotificationAdapter(IdentityNotificationPort):
    """
    Реализация IdentityNotificationPort.

    Формирует email-сообщения для Identity BC через Jinja2-шаблоны
    и делегирует отправку через shared EmailPort.

    Аргументы конструктора:
        email_port: Shared EmailPort (SMTP-адаптер).
        frontend_base_url: Базовый URL фронтенда для ссылок в письмах.
    """

    def __init__(self, email_port: EmailPort, frontend_base_url: str) -> None:
        self._email = email_port
        self._frontend_url = frontend_base_url.rstrip("/")
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=True,
        )

    def _render(self, template_name: str, **ctx: Any) -> tuple[str, str]:
        """Рендерить пару (body, html_body) из .txt и .html шаблонов."""
        body = self._env.get_template(f"{template_name}.txt").render(**ctx)
        html_body = self._env.get_template(f"{template_name}.html").render(**ctx)
        return body, html_body

    async def _send(self, to: str, subject: str, template_name: str, **ctx: Any) -> None:
        body, html_body = self._render(template_name, **ctx)
        await self._email.send(
            EmailMessage(
                to=(to,),
                subject=subject,
                body=body,
                html_body=html_body,
            )
        )

    async def send_email_verification(
        self, email: str, user_id: str, token: str
    ) -> None:
        link = f"{self._frontend_url}/verify-email?user_id={user_id}&token={token}"
        await self._send(
            to=email,
            subject="Подтверждение email-адреса",
            template_name="email_verification",
            link=link,
        )
        logger.info("Email verification sent", email=email, user_id=user_id)

    async def send_password_reset(self, email: str, token: str) -> None:
        link = f"{self._frontend_url}/reset-password?token={token}"
        await self._send(
            to=email,
            subject="Сброс пароля",
            template_name="password_reset",
            link=link,
        )
        logger.info("Password reset email sent", email=email)

    async def send_password_changed_notification(self, email: str) -> None:
        await self._send(
            to=email,
            subject="Пароль изменён",
            template_name="password_changed",
        )
        logger.info("Password changed notification sent", email=email)

    async def send_new_device_login_alert(
        self, email: str, ip: str, device: str
    ) -> None:
        await self._send(
            to=email,
            subject="Вход с нового устройства",
            template_name="new_device_login",
            ip=ip,
            device=device,
        )
        logger.info("New device login alert sent", email=email, ip=ip)

    async def send_account_deletion_requested(self, email: str) -> None:
        await self._send(
            to=email,
            subject="Запрос на удаление аккаунта",
            template_name="account_deletion_requested",
        )
        logger.info("Account deletion requested notification sent", email=email)

    async def send_account_locked_notification(
        self, email: str, locked_until: str | None
    ) -> None:
        await self._send(
            to=email,
            subject="Аккаунт заблокирован",
            template_name="account_locked",
            locked_until=locked_until,
        )
        logger.info("Account locked notification sent", email=email, locked_until=locked_until)
