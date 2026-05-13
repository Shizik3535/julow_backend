from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class TimeEntryDTO(BaseDTO):
    """
    DTO записи времени (TimeTracking BC).

    Атрибуты:
        id: Идентификатор записи.
        user_id: ID пользователя.
        workspace_id: ID workspace.
        task_id: ID задачи.
        project_id: ID проекта.
        epic_id: ID эпика.
        description: Описание.
        timer_state: Состояние таймера (running/paused/stopped).
        status: Статус записи (draft/submitted/approved/rejected/locked).
        started_at: Время старта таймера.
        stopped_at: Время остановки таймера.
        duration_seconds: Длительность в секундах.
        entry_date: Дата записи (ISO).
        is_billable: Оплачиваемая ли.
        hourly_rate: Почасовая ставка (amount + currency).
        category_id: ID категории.
        tag_ids: Список ID тегов.
        time_logs: Детализация таймера.
        rejection_reason: Причина отклонения.
        rounding_config: Конфигурация округления.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: str
    user_id: str
    workspace_id: str
    task_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str | None = None
    timer_state: str = "stopped"
    status: str = "draft"
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    duration_seconds: int = 0
    entry_date: str = ""
    is_billable: bool = False
    hourly_rate: dict[str, Any] | None = None
    category_id: str | None = None
    tag_ids: list[str] = []
    time_logs: list[dict[str, Any]] = []
    rejection_reason: dict[str, Any] | None = None
    rounding_config: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TimeEntryListDTO(BaseDTO):
    """Список записей времени с total."""

    items: list[TimeEntryDTO]
    total: int
