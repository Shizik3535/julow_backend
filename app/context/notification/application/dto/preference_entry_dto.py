from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class PreferenceEntryDTO(BaseDTO):
    """
    DTO записи настройки уведомлений.

    Атрибуты:
        type: Тип уведомления.
        in_app: Включён ли in-app канал.
        email: Включён ли email канал.
        push: Включён ли push канал.
        webhook: Включён ли webhook канал.
    """

    type: str = ""
    in_app: bool = True
    email: bool = False
    push: bool = False
    webhook: bool = False
