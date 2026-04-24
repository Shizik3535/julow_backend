from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.application.ports.notification.email_dto import EmailMessage


class EmailPort(ABC):
    """
    Порт (интерфейс) для отправки email.

    Абстрагирует работу с SMTP-серверами.
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        send: Отправить email-письмо.

    Правила:
        - Email отправляется асинхронно
        - Ошибки отправки логируются, но не ломают основной поток
        - Поддерживается как plain text, так и HTML
    """

    @abstractmethod
    async def send(self, message: EmailMessage) -> None:
        """
        Отправить email.

        Аргументы:
            message: Email-сообщение для отправки.
        """
