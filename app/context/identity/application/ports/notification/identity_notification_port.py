from __future__ import annotations

from abc import ABC, abstractmethod


class IdentityNotificationPort(ABC):
    """
    BC-специфичный порт для отправки уведомлений Identity BC.

    Абстрагирует отправку email-уведомлений, связанных
    с аутентификацией и управлением аккаунтом.

    Handler'ы вызывают доменно-специфичные методы, а реализация
    (адаптер) в infrastructure-слое формирует шаблоны и отправляет
    через shared ``EmailPort``.
    """

    @abstractmethod
    async def send_email_verification(
        self, email: str, user_id: str, token: str
    ) -> None:
        """
        Отправить письмо подтверждения email.

        Аргументы:
            email: Адрес получателя.
            user_id: ID пользователя.
            token: Токен верификации.
        """

    @abstractmethod
    async def send_password_reset(self, email: str, token: str) -> None:
        """
        Отправить письмо сброса пароля.

        Аргументы:
            email: Адрес получателя.
            token: Токен сброса пароля.
        """

    @abstractmethod
    async def send_password_changed_notification(self, email: str) -> None:
        """
        Уведомить пользователя об успешной смене пароля.

        Аргументы:
            email: Адрес получателя.
        """

    @abstractmethod
    async def send_new_device_login_alert(
        self, email: str, ip: str, device: str
    ) -> None:
        """
        Уведомить пользователя о входе с нового устройства/IP.

        Аргументы:
            email: Адрес получателя.
            ip: IP-адрес, с которого был выполнен вход.
            device: User-Agent устройства.
        """

    @abstractmethod
    async def send_account_deletion_requested(self, email: str) -> None:
        """
        Уведомить пользователя о запросе удаления аккаунта.

        Аргументы:
            email: Адрес получателя.
        """

    @abstractmethod
    async def send_account_locked_notification(
        self, email: str, locked_until: str | None
    ) -> None:
        """
        Уведомить пользователя о блокировке аккаунта.

        Аргументы:
            email: Адрес получателя.
            locked_until: Время разблокировки (ISO 8601) или None.
        """
