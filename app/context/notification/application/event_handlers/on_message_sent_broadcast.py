"""Обработчик события ``MessageSent`` → live-broadcast по WebSocket.

Назначение
==========

В отличие от :class:`OnMessageSentNotify`, который создаёт IN_APP-уведомление
с уважением к настройкам пользователя (DND, prefs), этот обработчик шлёт
**гарантированный** WS-кадр с типом ``chat.message.created`` всем участникам
чата (включая отправителя — для подтверждения доставки на других вкладках).

Зачем нужен отдельный обработчик
================================

Realtime-доставка сообщений в открытом чате — это часть ядра UX: если у
получателя выключен IN_APP для CHAT_MESSAGE, он всё равно ОЖИДАЕТ увидеть
новое сообщение в активном чате. Уведомления — это о пушах/бейджах, а
ленту чата нельзя замалчивать.

Поэтому здесь мы:

* НЕ создаём ``Notification`` (это делает ``OnMessageSentNotify``);
* НЕ проверяем prefs / DND;
* шлём в WebSocket компактный payload, по которому фронт делает
  ``listMessages(chat_id)`` и обновляет UI.

Frontend
========

``chats-page.tsx`` подписан на ``chat.message.created`` через
``subscribeWsEvent`` и при получении обновляет ``messagesByChat`` для
известных чатов и `last_message_at` для превью.
"""

from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.ports.notification.websocket_dto import (
    WebSocketMessage,
)
from app.shared.application.ports.notification.websocket_port import (
    WebSocketPort,
)
from app.context.notification.application.ports.integration.inboard.chat_members_port import (
    ChatMembersPort,
)


class OnMessageSentBroadcastWs(BaseEventHandler[dict[str, Any]]):
    """Шлёт WS-кадр ``chat.message.created`` всем участникам чата."""

    def __init__(
        self,
        websocket_port: WebSocketPort,
        chat_members_port: ChatMembersPort,
    ) -> None:
        super().__init__()
        self._ws = websocket_port
        self._members_port = chat_members_port

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "MessageSent":
            return
        payload = event.get("payload", {})
        message_id = payload.get("message_id", "")
        chat_id = payload.get("chat_id", "")
        sender_id = payload.get("sender_id", "")
        message_type = payload.get("message_type", "text")

        if not message_id or not chat_id:
            return

        # Системные сообщения (например, «X добавлен в чат») транслируем
        # тоже — это валидный апдейт ленты чата.
        member_ids = await self._members_port.get_chat_member_ids(chat_id)
        if not member_ids:
            return

        ws_message = WebSocketMessage(
            event_type="chat.message.created",
            payload={
                "chat_id": chat_id,
                "message_id": message_id,
                "sender_id": sender_id,
                "message_type": (
                    message_type.value
                    if hasattr(message_type, "value")
                    else str(message_type)
                ),
            },
        )

        for user_id in member_ids:
            try:
                await self._ws.send_to_user(user_id, ws_message)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning(
                    "chat.message.created WS send failed",
                    user_id=user_id,
                    chat_id=chat_id,
                    error=str(exc),
                )
