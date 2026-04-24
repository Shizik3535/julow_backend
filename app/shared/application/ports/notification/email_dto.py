from __future__ import annotations

from typing import Any

from app.shared.application.base_dto import BaseDTO


class EmailMessage(BaseDTO):
    """
    Email-сообщение.

    Атрибуты:
        to: Список адресатов.
        subject: Тема письма.
        body: Текстовое содержимое письма.
        html_body: HTML-содержимое письма (опционально).
        cc: Список CC-адресатов.
        bcc: Список BCC-адресатов.
        reply_to: Адрес для ответа.
        attachments: Вложения (опционально).
    """

    to: tuple[str, ...]
    subject: str
    body: str
    html_body: str | None = None
    cc: tuple[str, ...] = ()
    bcc: tuple[str, ...] = ()
    reply_to: str | None = None
    attachments: tuple[dict[str, Any], ...] = ()
