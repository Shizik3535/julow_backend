from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReorderBoardColumnsRequest(BaseModel):
    """Запрос на переупорядочивание колонок доски."""

    model_config = ConfigDict(from_attributes=True)

    column_ids: list[str] = Field(..., description="Список UUID колонок в новом порядке")
