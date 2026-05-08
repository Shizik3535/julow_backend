"""Адаптер ConferenceProviderPort для ручных ссылок (MANUAL).

Не общается ни с какой внешней системой — просто оборачивает URL,
который пользователь вставил вручную.
"""

from __future__ import annotations

from app.context.communication.application.ports.integration.inboard.conference_provider_port import (
    ConferenceJoinTokenDTO,
    ConferenceProviderPort,
    ConferenceRoomDTO,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)


class ManualLinkConferenceAdapter(ConferenceProviderPort):
    """Реализация для провайдера ``MANUAL`` — пользовательская ссылка."""

    async def create_room(
        self,
        meeting_id: str,
        organizer_id: str,
        manual_url: str | None = None,
    ) -> ConferenceRoomDTO:
        return ConferenceRoomDTO(
            provider=ConferenceProvider.MANUAL.value,
            external_id=None,
            join_url=manual_url,
        )

    async def generate_join_token(
        self,
        external_id: str | None,
        manual_url: str | None,
        user_id: str,
        is_organizer: bool,
    ) -> ConferenceJoinTokenDTO:
        if not manual_url:
            raise ValueError(
                "Для MANUAL-провайдера требуется заранее заданный conference_url"
            )
        return ConferenceJoinTokenDTO(join_url=manual_url, access_token=None)

    async def delete_room(self, external_id: str | None) -> None:
        # Нечего удалять — комната «живёт» во внешней системе пользователя.
        return None
