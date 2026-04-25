from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AddAutomationRuleRequest(BaseModel):
    """Запрос на добавление правила автоматизации."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200, description="Название правила")
    trigger: str = Field(..., description="Триггер: status_changed | assignee_changed | due_date_approaching | ...")
    action: str = Field(..., description="Действие: assign_user | change_status | add_label | ...")
    action_params: dict[str, Any] = Field(default_factory=dict, description="Параметры действия")
