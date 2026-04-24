from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BackupCodesResponse(BaseModel):
    """
    Ответ с резервными кодами 2FA.

    Содержит plain-коды, которые показываются пользователю
    один раз при генерации. Не хранятся в системе.

    Атрибуты:
        codes: Список резервных кодов в открытом виде.
    """

    model_config = ConfigDict(from_attributes=True)

    codes: list[str] = Field(
        ...,
        description="Список резервных кодов (показываются один раз)",
        examples=[["A1B2C3D4", "E5F6G7H8", "I9J0K1L2"]],
    )
