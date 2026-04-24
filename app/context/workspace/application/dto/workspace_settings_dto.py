from __future__ import annotations

from typing import Any

from app.shared.application.base_dto import BaseDTO


class WorkspaceSettingsDTO(BaseDTO):
    """
    DTO настроек workspace — проекция политик и лимитов (Workspace BC).

    Используется outboard-провайдером для предоставления
    настроек другим BC.

    Атрибуты:
        workspace_id: ID workspace.
        security_policy: Политика безопасности (dict).
        membership_policy: Политика членства (dict).
        limits: Лимиты workspace (dict).
    """

    workspace_id: str
    security_policy: dict[str, Any]
    membership_policy: dict[str, Any]
    limits: dict[str, Any]
