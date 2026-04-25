from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BoardColumnResponse(BaseModel):
    """Данные колонки доски."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID колонки")
    name: str = Field(..., description="Название колонки")
    order: int = Field(..., description="Порядок колонки")
    color: str | None = Field(None, description="Цвет колонки (HEX)")
    wip_limit: int | None = Field(None, description="WIP-лимит")
    status_mapping: str | None = Field(None, description="UUID workflow-статуса для маппинга")


class SwimlaneResponse(BaseModel):
    """Данные swimlane."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID swimlane")
    name: str = Field(..., description="Название swimlane")
    order: int = Field(..., description="Порядок swimlane")
    group_by: str = Field(..., description="Тип группировки: assignee | priority | label | epic | custom_field")
    group_value: str | None = Field(None, description="Значение группировки")


class WorkflowStatusResponse(BaseModel):
    """Данные workflow-статуса."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID статуса")
    name: str = Field(..., description="Название статуса")
    color: str | None = Field(None, description="Цвет статуса (HEX)")
    icon: str | None = Field(None, description="Иконка статуса")
    order: int = Field(..., description="Порядок статуса")
    is_default: bool = Field(..., description="Является ли начальным статусом")
    category: str = Field(..., description="Категория: todo | in_progress | done | cancelled | blocked | review")


class WorkflowTransitionResponse(BaseModel):
    """Данные перехода между статусами."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID перехода")
    from_status_id: str = Field(..., description="UUID исходного статуса")
    to_status_id: str = Field(..., description="UUID целевого статуса")
    name: str = Field(..., description="Название перехода")
    required_permission: str | None = Field(None, description="Требуемое право для перехода")


class ProjectViewResponse(BaseModel):
    """Данные сохранённого представления."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID представления")
    name: str = Field(..., description="Название представления")
    config: dict[str, Any] | None = Field(None, description="Конфигурация представления")
    is_default: bool = Field(..., description="Является ли представлением по умолчанию")
    is_shared: bool = Field(..., description="Является ли общим представлением")
    owner_id: str | None = Field(None, description="UUID владельца (None — общее)")


class AutomationRuleResponse(BaseModel):
    """Данные правила автоматизации."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID правила")
    name: str = Field(..., description="Название правила")
    trigger: str = Field(..., description="Триггер: status_changed | assignee_changed | due_date_approaching | ...")
    action: str = Field(..., description="Действие: assign_user | change_status | add_label | ...")
    action_params: dict[str, Any] = Field(default_factory=dict, description="Параметры действия")
    is_enabled: bool = Field(..., description="Включено ли правило")


class BoardResponse(BaseModel):
    """Ответ с данными доски проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID доски")
    project_id: str = Field(..., description="UUID проекта")
    columns: list[BoardColumnResponse] = Field(default_factory=list, description="Колонки доски")
    swimlanes: list[SwimlaneResponse] = Field(default_factory=list, description="Swimlanes")
    workflow_statuses: list[WorkflowStatusResponse] = Field(default_factory=list, description="Workflow-статусы")
    workflow_transitions: list[WorkflowTransitionResponse] = Field(
        default_factory=list, description="Переходы между статусами"
    )
    views: list[ProjectViewResponse] = Field(default_factory=list, description="Сохранённые представления")
    automation_rules: list[AutomationRuleResponse] = Field(
        default_factory=list, description="Правила автоматизации"
    )
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
