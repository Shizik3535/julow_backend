from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiosmtplib

from app.core.logging import get_logger
from app.shared.application.ports.notification.email_dto import EmailMessage
from app.shared.application.ports.notification.email_port import EmailPort

logger = get_logger(__name__)


class SmtpEmailAdapter(EmailPort):
    """
    Реализация EmailPort на основе aiosmtplib.

    Отправляет email через SMTP-сервер с поддержкой
    plain text, HTML и вложений.
    В dev-режиме — Mailpit (localhost:1025).
    В prod — релей через SendGrid/SES.

    Аргументы конструктора:
        host: Адрес SMTP-сервера.
        port: Порт SMTP-сервера.
        username: Имя пользователя (опционально).
        password: Пароль (опционально).
        use_tls: Использовать TLS.
        from_email: Email-адрес отправителя по умолчанию.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = False,
        from_email: str = "noreply@julow.com",
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._from_email = from_email

    async def send(self, message: EmailMessage) -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = self._from_email
        msg["To"] = ", ".join(message.to)
        msg["Subject"] = message.subject

        if message.cc:
            msg["Cc"] = ", ".join(message.cc)
        if message.bcc:
            msg["Bcc"] = ", ".join(message.bcc)
        if message.reply_to:
            msg["Reply-To"] = message.reply_to

        msg.attach(MIMEText(message.body, "plain", "utf-8"))
        if message.html_body:
            msg.attach(MIMEText(message.html_body, "html", "utf-8"))

        recipients = list(message.to)
        if message.cc:
            recipients.extend(message.cc)
        if message.bcc:
            recipients.extend(message.bcc)

        try:
            await aiosmtplib.send(
                msg,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                use_tls=self._use_tls,
            )
            logger.info("Email sent", to=message.to, subject=message.subject)
        except Exception as e:
            logger.error("Email send failed", to=message.to, subject=message.subject, error=str(e))
            raise
