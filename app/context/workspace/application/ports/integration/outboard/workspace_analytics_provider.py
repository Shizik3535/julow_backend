from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkspaceAnalyticsProvider(ABC):
    """
    Outboard-порт: агрегационные данные workspace для Analytics BC.

    Реализуется в infrastructure-слое Workspace BC. Возвращает плоские
    табличные строки (``list[dict[str, Any]]``) с заранее зафиксированным
    набором имён колонок (см. docstring метода) — резолвер Analytics
    переименует ключи в alias-ы метрик/измерений.

    Контракт умышленно «толстый»: все варианты группировки/фильтрации
    проходят через единственный метод, а не через generic-getter.
    Это удерживает SQL внутри Workspace BC и оставляет за ним права
    на оптимизацию (индексы/материализация).
    """

    @abstractmethod
    async def list_workspaces(
        self,
        *,
        workspace_ids: list[str] | None = None,
        organization_id: str | None = None,
        statuses: list[str] | None = None,
        types: list[str] | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Вернуть список/агрегацию workspace-данных.

        Поддерживаемые поля фильтрации: ``workspace_ids``, ``organization_id``,
        ``statuses``, ``types``.
        Поддерживаемые поля группировки: ``status``, ``workspace_type``,
        ``organization_id``.
        Поддерживаемые поля сортировки: те же, что у группировки, плюс
        ``count`` (число строк в группе).

        Возвращает строки с фиксированными ключами:
            - без ``group_by`` — ``id``, ``name``, ``status``,
              ``workspace_type``, ``organization_id``, ``created_at``;
            - с ``group_by`` — ключи из ``group_by`` + ``count``.
        """
