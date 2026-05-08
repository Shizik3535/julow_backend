from __future__ import annotations

from enum import Enum


class ConferenceProvider(Enum):
    """
    Провайдер видеоконференции для совещания.

    Абстракция от конкретной реализации: домен хранит признак провайдера,
    инфраструктура (ConferenceProviderPort) знает, как с ним работать.

    Значения:
        MANUAL: Внешняя ссылка, вставленная пользователем (Zoom/Telemost/Meet/Teams и т.п.).
        INTERNAL: Встроенный WebRTC сервис (LiveKit/Janus/...).
        ZOOM: Интеграция с Zoom через OAuth + API.
        TELEMOST: Интеграция с Yandex Telemost.
        GOOGLE_MEET: Интеграция с Google Meet.
        TEAMS: Интеграция с Microsoft Teams.

    Правила:
        - MANUAL — самый базовый: ``conference_url`` обязателен и заполняется руками.
        - INTERNAL и интеграции — ``conference_url`` и ``conference_room_id``
          выставляются адаптером ``ConferenceProviderPort.create_room``.
    """

    MANUAL = "manual"
    INTERNAL = "internal"
    ZOOM = "zoom"
    TELEMOST = "telemost"
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"
