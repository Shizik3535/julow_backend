"""Интеграционные тесты NtfyPushAdapter (httpx + respx mock)."""

import uuid

import httpx
import pytest
import respx

from app.shared.application.ports.notification.push_dto import PushMessage
from app.shared.infrastructure.notification.ntfy_push_adapter import NtfyPushAdapter

NTFY_BASE_URL = "https://ntfy.example.com"


@pytest.mark.integration
class TestNtfyPushAdapter:
    """Тесты push-уведомлений через ntfy."""

    @pytest.fixture
    def http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient()

    @pytest.fixture
    def adapter(self, http_client: httpx.AsyncClient) -> NtfyPushAdapter:
        return NtfyPushAdapter(base_url=NTFY_BASE_URL, http_client=http_client)

    # ── send ─────────────────────────────────────────────────────────────

    @respx.mock
    async def test_send_push(self, adapter: NtfyPushAdapter) -> None:
        recipient_id = uuid.uuid4()
        route = respx.post(f"{NTFY_BASE_URL}/{recipient_id}").mock(
            return_value=httpx.Response(200),
        )

        msg = PushMessage(
            recipient_id=recipient_id,
            title="Test Title",
            body="Test Body",
        )
        await adapter.send(msg)

        assert route.called
        request = route.calls.last.request
        assert request.headers["Title"] == "Test Title"
        assert request.content == b"Test Body"

    @respx.mock
    async def test_send_push_with_data(self, adapter: NtfyPushAdapter) -> None:
        recipient_id = uuid.uuid4()
        route = respx.post(f"{NTFY_BASE_URL}/{recipient_id}").mock(
            return_value=httpx.Response(200),
        )

        msg = PushMessage(
            recipient_id=recipient_id,
            title="With Data",
            body="Body",
            data={"action": "open", "url": "https://example.com"},
        )
        await adapter.send(msg)

        assert route.called
        request = route.calls.last.request
        assert request.headers["Title"] == "With Data"
        assert "Tags" in request.headers

    @respx.mock
    async def test_send_push_without_data_no_tags_header(self, adapter: NtfyPushAdapter) -> None:
        recipient_id = uuid.uuid4()
        route = respx.post(f"{NTFY_BASE_URL}/{recipient_id}").mock(
            return_value=httpx.Response(200),
        )

        msg = PushMessage(
            recipient_id=recipient_id,
            title="No Data",
            body="Body",
        )
        await adapter.send(msg)

        assert route.called
        assert "Tags" not in route.calls.last.request.headers

    @respx.mock
    async def test_send_raises_on_http_error(self, adapter: NtfyPushAdapter) -> None:
        recipient_id = uuid.uuid4()
        respx.post(f"{NTFY_BASE_URL}/{recipient_id}").mock(
            return_value=httpx.Response(500),
        )

        msg = PushMessage(
            recipient_id=recipient_id,
            title="Error",
            body="Should fail",
        )
        with pytest.raises(httpx.HTTPStatusError):
            await adapter.send(msg)

    # ── send_to_topic ────────────────────────────────────────────────────

    @respx.mock
    async def test_send_to_topic(self, adapter: NtfyPushAdapter) -> None:
        route = respx.post(f"{NTFY_BASE_URL}/my-topic").mock(
            return_value=httpx.Response(200),
        )

        await adapter.send_to_topic("my-topic", "Topic Title", "Topic Body")

        assert route.called
        request = route.calls.last.request
        assert request.headers["Title"] == "Topic Title"
        assert request.content == b"Topic Body"

    @respx.mock
    async def test_send_to_topic_with_data(self, adapter: NtfyPushAdapter) -> None:
        route = respx.post(f"{NTFY_BASE_URL}/data-topic").mock(
            return_value=httpx.Response(200),
        )

        await adapter.send_to_topic("data-topic", "T", "B", data={"key": "val"})

        assert route.called
        assert "Tags" in route.calls.last.request.headers

    @respx.mock
    async def test_send_to_topic_without_data(self, adapter: NtfyPushAdapter) -> None:
        route = respx.post(f"{NTFY_BASE_URL}/plain-topic").mock(
            return_value=httpx.Response(200),
        )

        await adapter.send_to_topic("plain-topic", "Title", "Body")

        assert route.called
        assert "Tags" not in route.calls.last.request.headers

    # ── send_batch ───────────────────────────────────────────────────────

    @respx.mock
    async def test_send_batch(self, adapter: NtfyPushAdapter) -> None:
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        route1 = respx.post(f"{NTFY_BASE_URL}/{id1}").mock(
            return_value=httpx.Response(200),
        )
        route2 = respx.post(f"{NTFY_BASE_URL}/{id2}").mock(
            return_value=httpx.Response(200),
        )

        messages = (
            PushMessage(recipient_id=id1, title="Batch 1", body="B1"),
            PushMessage(recipient_id=id2, title="Batch 2", body="B2"),
        )
        await adapter.send_batch(messages)

        assert route1.called
        assert route2.called

    @respx.mock
    async def test_send_batch_empty(self, adapter: NtfyPushAdapter) -> None:
        await adapter.send_batch(())

    @respx.mock
    async def test_send_batch_continues_on_partial_failure(self, adapter: NtfyPushAdapter) -> None:
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        respx.post(f"{NTFY_BASE_URL}/{id1}").mock(
            return_value=httpx.Response(500),
        )
        route2 = respx.post(f"{NTFY_BASE_URL}/{id2}").mock(
            return_value=httpx.Response(200),
        )

        messages = (
            PushMessage(recipient_id=id1, title="Fail", body="F"),
            PushMessage(recipient_id=id2, title="OK", body="O"),
        )
        # send_batch ловит ошибки и продолжает
        await adapter.send_batch(messages)

        assert route2.called

    # ── URL формирование ─────────────────────────────────────────────────

    @respx.mock
    async def test_base_url_trailing_slash_stripped(self, http_client: httpx.AsyncClient) -> None:
        adapter = NtfyPushAdapter(base_url=f"{NTFY_BASE_URL}/", http_client=http_client)
        recipient_id = uuid.uuid4()

        route = respx.post(f"{NTFY_BASE_URL}/{recipient_id}").mock(
            return_value=httpx.Response(200),
        )

        msg = PushMessage(
            recipient_id=recipient_id,
            title="Slash",
            body="Test",
        )
        await adapter.send(msg)

        assert route.called
