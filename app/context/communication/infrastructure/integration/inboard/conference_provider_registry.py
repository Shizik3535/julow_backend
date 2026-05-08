"""Реестр адаптеров ConferenceProviderPort по типу провайдера.

Команды Application-слоя инжектят реестр и берут нужный адаптер
по значению ``ConferenceProvider``. Для нереализованных провайдеров
поднимается ``ConferenceProviderNotImplementedException``.
"""

from __future__ import annotations

from app.context.communication.application.exceptions.authorization_exceptions import (
    ConferenceProviderNotImplementedException,
)
from app.context.communication.application.ports.integration.inboard.conference_provider_port import (
    ConferenceProviderPort,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)


class ConferenceProviderRegistry:
    """
    Маппинг ``ConferenceProvider → ConferenceProviderPort``.

    Адаптеры регистрируются на этапе DI-сборки. Если для запрошенного
    провайдера адаптера нет, поднимается ``ConferenceProviderNotImplementedException``.
    """

    def __init__(
        self,
        adapters: dict[ConferenceProvider, ConferenceProviderPort],
    ) -> None:
        self._adapters = adapters

    def get(self, provider: ConferenceProvider) -> ConferenceProviderPort:
        adapter = self._adapters.get(provider)
        if adapter is None:
            raise ConferenceProviderNotImplementedException(provider=provider.value)
        return adapter
