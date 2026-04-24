from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class BackupCodesResultDTO(BaseDTO):
    """
    DTO результата генерации резервных кодов (Identity BC).

    Содержит plain-коды, которые показываются пользователю
    один раз при генерации. Не хранятся в системе.

    Атрибуты:
        codes: Список резервных кодов в открытом виде.
    """

    codes: list[str]
