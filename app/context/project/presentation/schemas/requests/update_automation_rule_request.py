from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UpdateAutomationRuleRequest(BaseModel):
    """Запрос на обновление правила автоматизации."""

    model_config = ConfigDict(from_attributes=True)

    is_enabled: bool | None = Field(None, description="Включить/выключить правило")
    action_params: dict[str, str] | None = Field(None, description="Новые параметры действия")
