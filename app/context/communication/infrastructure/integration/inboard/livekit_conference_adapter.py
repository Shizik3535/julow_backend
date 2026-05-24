"""Адаптер ConferenceProviderPort для LiveKit (INTERNAL).

Использует ``livekit-api`` для:
    - создания комнат через LiveKit Room Service API;
    - генерации JWT-токенов (access_token) для подключения участников;
    - удаления комнат при отмене совещания.

Токен содержит grants на join + publish/subscribe. Браузер подключается
напрямую к LiveKit по ``public_url`` (WebSocket), обходя backend.
"""

from __future__ import annotations

import datetime
import logging

from livekit.api import AccessToken, LiveKitAPI, VideoGrants
from livekit.protocol.room import CreateRoomRequest, DeleteRoomRequest

from app.context.communication.application.ports.integration.inboard.conference_provider_port import (
    ConferenceJoinTokenDTO,
    ConferenceProviderPort,
    ConferenceRoomDTO,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)

logger = logging.getLogger(__name__)


class LiveKitConferenceAdapter(ConferenceProviderPort):
    """Реализация ConferenceProviderPort для встроенного WebRTC (LiveKit).

    Параметры конструктора:
        livekit_url: HTTP-адрес LiveKit внутри docker-сети (например
            ``http://livekit:7880``). Используется Room Service API.
        api_key: API-ключ из livekit.yaml → ``keys``.
        api_secret: Секрет, парный к API-ключу.
        public_url: WebSocket URL, который увидит браузер клиента
            (``ws://localhost:7880`` для dev, ``wss://livekit.julow.ru`` для prod).
    """

    def __init__(
        self,
        livekit_url: str,
        api_key: str,
        api_secret: str,
        public_url: str,
    ) -> None:
        self._url = livekit_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._public_url = public_url

    async def create_room(
        self,
        meeting_id: str,
        organizer_id: str,
        manual_url: str | None = None,
    ) -> ConferenceRoomDTO:
        room_name = f"meeting-{meeting_id}"
        try:
            lk = LiveKitAPI(url=self._url, api_key=self._api_key, api_secret=self._api_secret)
            await lk.room.create_room(
                CreateRoomRequest(
                    name=room_name,
                    empty_timeout=600,     # 10 мин — автоудаление пустой комнаты
                    max_participants=50,
                )
            )
            await lk.aclose()
        except Exception:
            logger.exception("LiveKit: failed to create room %s", room_name)

        return ConferenceRoomDTO(
            provider=ConferenceProvider.INTERNAL.value,
            external_id=room_name,
            join_url=self._public_url,
        )

    async def generate_join_token(
        self,
        external_id: str | None,
        manual_url: str | None,
        user_id: str,
        is_organizer: bool,
        user_display_name: str | None = None,
    ) -> ConferenceJoinTokenDTO:
        room_name = external_id or ""
        display = user_display_name or user_id
        token = (
            AccessToken(api_key=self._api_key, api_secret=self._api_secret)
            .with_identity(user_id)
            .with_name(display)
            .with_grants(
                VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )
            .with_ttl(datetime.timedelta(hours=4))
        )
        jwt = token.to_jwt()
        return ConferenceJoinTokenDTO(
            join_url=self._public_url,
            access_token=jwt,
        )

    async def delete_room(self, external_id: str | None) -> None:
        if not external_id:
            return
        try:
            lk = LiveKitAPI(url=self._url, api_key=self._api_key, api_secret=self._api_secret)
            await lk.room.delete_room(DeleteRoomRequest(room=external_id))
            await lk.aclose()
        except Exception:
            logger.warning("LiveKit: failed to delete room %s", external_id, exc_info=True)
