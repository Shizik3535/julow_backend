"""Интеграционные тесты IdentityNotificationAdapter (реальный SMTP → MailHog)."""

from email.header import decode_header

import pytest
import httpx

from app.context.identity.infrastructure.notification.identity_notification_adapter import (
    IdentityNotificationAdapter,
)
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter


MAILHOG_API = "http://localhost:8025/api/v2/messages"


@pytest.mark.integration
class TestIdentityNotificationAdapter:
    """Тесты Identity уведомлений через SMTP → MailHog."""

    @pytest.fixture
    def email_port(self, smtp_host: str, smtp_port: int) -> SmtpEmailAdapter:
        return SmtpEmailAdapter(
            host=smtp_host,
            port=smtp_port,
            username=None,
            password=None,
            use_tls=False,
        )

    @pytest.fixture
    def adapter(self, email_port: SmtpEmailAdapter) -> IdentityNotificationAdapter:
        return IdentityNotificationAdapter(
            email_port=email_port,
            frontend_base_url="http://localhost:3000",
        )

    @staticmethod
    async def _clear_mailhog() -> None:
        async with httpx.AsyncClient() as client:
            await client.delete("http://localhost:8025/api/v1/messages")

    @staticmethod
    async def _get_latest_message() -> dict | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(MAILHOG_API)
            items = resp.json().get("items", [])
            return items[0] if items else None

    @staticmethod
    def _decode_subject(msg: dict) -> str:
        raw = msg["Content"]["Headers"]["Subject"][0]
        parts = decode_header(raw)
        return "".join(
            part.decode(enc or "utf-8") if isinstance(part, bytes) else part
            for part, enc in parts
        )

    async def test_send_email_verification(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_email_verification(
            email="new@example.com", user_id="user-123", token="verify-token-456"
        )
        msg = await self._get_latest_message()
        assert msg is not None
        assert "new@example.com" in msg["Content"]["Headers"]["To"][0]
        assert "Подтверждение" in self._decode_subject(msg)

    async def test_send_password_reset(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_password_reset(email="reset@example.com", token="reset-token")
        msg = await self._get_latest_message()
        assert msg is not None
        assert "Сброс пароля" in self._decode_subject(msg)

    async def test_send_password_changed_notification(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_password_changed_notification(email="changed@example.com")
        msg = await self._get_latest_message()
        assert msg is not None
        assert "Пароль изменён" in self._decode_subject(msg)

    async def test_send_new_device_login_alert(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_new_device_login_alert(
            email="alert@example.com", ip="192.168.1.100", device="Chrome/Windows"
        )
        msg = await self._get_latest_message()
        assert msg is not None
        assert "нового устройства" in self._decode_subject(msg)

    async def test_send_account_deletion_requested(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_account_deletion_requested(email="delete@example.com")
        msg = await self._get_latest_message()
        assert msg is not None
        assert "удалени" in self._decode_subject(msg).lower()

    async def test_send_account_locked_notification(self, adapter: IdentityNotificationAdapter) -> None:
        await self._clear_mailhog()
        await adapter.send_account_locked_notification(
            email="locked@example.com", locked_until="2025-01-01T00:00:00Z"
        )
        msg = await self._get_latest_message()
        assert msg is not None
        assert "заблокирован" in self._decode_subject(msg).lower()
