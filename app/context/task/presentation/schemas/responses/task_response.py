from __future__ import annotations

from typing import Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LabelResponse(BaseModel):
    """Метка задачи."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Название метки")
    color: str | None = Field(default=None, description="Цвет (HEX)")


class ChecklistItemResponse(BaseModel):
    """Пункт чек-листа."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    is_checked: bool
    assignee_id: str | None = None
    due_date: str | None = None
    checked_at: str | None = None
    order: int


class ChecklistResponse(BaseModel):
    """Чек-лист задачи."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    items: list[ChecklistItemResponse] = Field(default_factory=list)


class RelationResponse(BaseModel):
    """Связь между задачами."""

    model_config = ConfigDict(from_attributes=True)

    related_task_id: str
    relation_type: str
    created_at: str
    created_by: str


class WatcherResponse(BaseModel):
    """Наблюдатель задачи."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    watched_at: str


class AttachmentResponse(BaseModel):
    """Вложение задачи."""

    model_config = ConfigDict(from_attributes=True)

    file_id: str
    filename: str
    size_bytes: int
    uploaded_by: str
    uploaded_at: str


class TaskResponse(BaseModel):
    """Ответ с данными задачи."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    parent_task_id: str | None = None
    epic_id: str | None = None
    title: str
    description: dict[str, str] | None = None
    status_id: str | None = None
    priority: str
    task_type: str
    assignee_ids: list[str] = Field(default_factory=list)
    reporter_id: str | None = None
    labels: list[LabelResponse] = Field(default_factory=list)
    progress: int
    effort_estimate: dict[str, Any] | None = None
    actual_effort: dict[str, Any] | None = None
    start_date: str | None = None
    due_date: str | None = None
    completed_at: datetime | None = None
    custom_fields: dict[str, str] = Field(default_factory=dict)
    checklists: list[ChecklistResponse] = Field(default_factory=list)
    relations: list[RelationResponse] = Field(default_factory=list)
    watchers: list[WatcherResponse] = Field(default_factory=list)
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    order: dict[str, Any] | None = None
    sprint_id: str | None = None
    status: str
    recurrence: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
