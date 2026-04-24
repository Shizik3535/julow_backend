from __future__ import annotations

from typing import Any

import httpx

from app.core.logging import get_logger
from app.shared.application.ports.notification.push_dto import PushMessage
from app.shared.application.ports.notification.push_port import PushPort

logger = get_logger(__name__)


class NtfyPushAdapter(PushPort):
    """
    Реализация PushPort на основе ntfy.sh.

    Отправляет push-уведомления через HTTP POST к ntfy-серверу.
    Поддерживает отправку пользователю (по теме = user_id),
    на произвольную тему и пакетную отправку.

    Аргументы конструктора:
        base_url: URL ntfy-сервера.
        http_client: Async HTTP клиент (httpx).
    """

    def __init__(self, base_url: str, http_client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = http_client

    async def send(self, message: PushMessage) -> None:
        topic = str(message.recipient_id)
        await self._send_to_ntfy(topic, message.title, message.body, message.data)
        logger.info("Push sent", recipient_id=message.recipient_id)

    async def send_to_topic(self, topic: str, title: str, body: str, data: dict[str, Any] | None = None) -> None:
        await self._send_to_ntfy(topic, title, body, data)
        logger.info("Push sent to topic", topic=topic)

    async def send_batch(self, messages: tuple[PushMessage, ...]) -> None:
        for message in messages:
            topic = str(message.recipient_id)
            try:
                await self._send_to_ntfy(topic, message.title, message.body, message.data)
            except Exception as e:
                logger.error(
                    "Batch push send failed",
                    recipient_id=message.recipient_id,
                    error=str(e),
                )
        logger.info("Batch push sent", count=len(messages))

    async def _send_to_ntfy(
        self,
        topic: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        url = f"{self._base_url}/{topic}"
        headers: dict[str, str] = {"Title": title}
        if data:
            headers["Tags"] = ",".join(str(v) for v in data.values())

        response = await self._client.post(url, content=body, headers=headers)
        response.raise_for_status()
