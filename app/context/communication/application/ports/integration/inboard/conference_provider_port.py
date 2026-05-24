from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ConferenceRoomDTO:
    """Результат создания/получения конференц-комнаты от провайдера.

    Атрибуты:
        provider: Идентификатор провайдера (значение enum ``ConferenceProvider``).
        external_id: ID комнаты во внешней системе (LiveKit room name, Zoom meeting id, ...).
            Может быть пустым для MANUAL.
        join_url: URL для подключения участника. Может быть None,
            если провайдер требует генерации URL по запросу join.
    """

    provider: str
    external_id: str | None
    join_url: str | None


@dataclass(frozen=True)
class ConferenceJoinTokenDTO:
    """Токен/URL для подключения конкретного участника к конференции.

    Атрибуты:
        join_url: URL для подключения (тот же для всех или с встроенным токеном).
        access_token: Токен доступа (например JWT для LiveKit). None — если не требуется.
    """

    join_url: str
    access_token: str | None = None


class ConferenceProviderPort(ABC):
    """
    Inboard-порт: абстракция над поставщиком видеоконференции.

    Адаптеры реализуют конкретные провайдеры (LiveKit, Zoom, Telemost,
    GoogleMeet, Teams, ManualLink). Все они работают через одинаковый
    набор методов, что позволяет домену оставаться нейтральным.

    Контракт:
        - ``create_room`` вызывается при создании Meeting; возвращает
          атрибуты комнаты, которые сохраняются в агрегате.
        - ``generate_join_token`` вызывается при подключении участника.
        - ``delete_room`` — при отмене/удалении совещания (best-effort).
    """

    @abstractmethod
    async def create_room(
        self,
        meeting_id: str,
        organizer_id: str,
        manual_url: str | None = None,
    ) -> ConferenceRoomDTO:
        """
        Создать конференц-комнату.

        Аргументы:
            meeting_id: ID совещания (для именования комнаты).
            organizer_id: ID организатора.
            manual_url: Заранее заданный URL (используется только для MANUAL provider).

        Возвращает:
            ``ConferenceRoomDTO`` с данными созданной комнаты.
        """

    @abstractmethod
    async def generate_join_token(
        self,
        external_id: str | None,
        manual_url: str | None,
        user_id: str,
        is_organizer: bool,
        user_display_name: str | None = None,
    ) -> ConferenceJoinTokenDTO:
        """
        Сгенерировать токен/URL для подключения пользователя.

        Аргументы:
            external_id: ID комнаты во внешней системе (None для MANUAL).
            manual_url: Сохранённый URL (используется для MANUAL).
            user_id: ID подключающегося пользователя.
            is_organizer: Является ли пользователь организатором.
            user_display_name: Отображаемое имя пользователя (для отображения в UI).
        """

    @abstractmethod
    async def delete_room(self, external_id: str | None) -> None:
        """Удалить комнату во внешней системе. Best-effort — ошибки игнорируются."""
