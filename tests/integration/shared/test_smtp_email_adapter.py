"""Интеграционные тесты SmtpEmailAdapter (реальный SMTP → MailHog)."""

import pytest
import httpx

from app.shared.application.ports.notification.email_dto import EmailMessage
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter


MAILHOG_API = "http://localhost:8025/api/v2/messages"


@pytest.mark.integration
class TestSmtpEmailAdapter:
    """Тесты отправки email через SMTP → MailHog."""

    @pytest.fixture
    def adapter(self, smtp_host: str, smtp_port: int) -> SmtpEmailAdapter:
        return SmtpEmailAdapter(
            host=smtp_host,
            port=smtp_port,
            username=None,
            password=None,
            use_tls=False,
            from_email="test@julow.com",
        )

    @staticmethod
    async def _clear_mailhog() -> None:
        async with httpx.AsyncClient() as client:
            await client.delete("http://localhost:8025/api/v1/messages")

    @staticmethod
    async def _get_mailhog_messages() -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(MAILHOG_API)
            data = resp.json()
            return data.get("items", [])

    async def test_send_plain_text_email(self, adapter: SmtpEmailAdapter) -> None:
        await self._clear_mailhog()

        msg = EmailMessage(
            to=("recipient@example.com",),
            subject="Test Plain",
            body="Hello, this is a test.",
        )
        await adapter.send(msg)

        messages = await self._get_mailhog_messages()
        assert len(messages) >= 1
        latest = messages[0]
        assert latest["Content"]["Headers"]["Subject"][0] == "Test Plain"
        assert "recipient@example.com" in latest["Content"]["Headers"]["To"][0]

    async def test_send_html_email(self, adapter: SmtpEmailAdapter) -> None:
        await self._clear_mailhog()

        msg = EmailMessage(
            to=("user@example.com",),
            subject="Test HTML",
            body="Plain fallback",
            html_body="<h1>Hello</h1><p>HTML content</p>",
        )
        await adapter.send(msg)

        messages = await self._get_mailhog_messages()
        assert len(messages) >= 1
        latest = messages[0]
        assert latest["Content"]["Headers"]["Subject"][0] == "Test HTML"

    async def test_send_email_with_cc(self, adapter: SmtpEmailAdapter) -> None:
        await self._clear_mailhog()

        msg = EmailMessage(
            to=("main@example.com",),
            subject="Test CC",
            body="With CC",
            cc=("cc@example.com",),
        )
        await adapter.send(msg)

        messages = await self._get_mailhog_messages()
        assert len(messages) >= 1
        latest = messages[0]
        assert "cc@example.com" in latest["Content"]["Headers"].get("Cc", [""])[0]

    async def test_from_address(self, adapter: SmtpEmailAdapter) -> None:
        await self._clear_mailhog()

        msg = EmailMessage(
            to=("someone@example.com",),
            subject="Test From",
            body="Check from address",
        )
        await adapter.send(msg)

        messages = await self._get_mailhog_messages()
        assert len(messages) >= 1
        latest = messages[0]
        assert "test@julow.com" in latest["Content"]["Headers"]["From"][0]
