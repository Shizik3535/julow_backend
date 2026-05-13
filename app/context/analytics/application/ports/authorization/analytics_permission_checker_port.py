from __future__ import annotations

from abc import ABC, abstractmethod


class AnalyticsPermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте Analytics BC.

    Analytics BC не содержит собственного агрегата ролей; проверка
    делегируется в Workspace BC (`WorkspaceMembershipProvider.has_permission`).

    Workspace-уровень permission-пространства:
        - `analytics.read`           — чтение дашбордов/отчётов/виджет-данных
        - `analytics.write`          — создание/изменение дашбордов/виджетов
        - `analytics.delete`         — удаление дашбордов
        - `analytics.share`          — шеринг дашбордов/отчётов
        - `analytics.report.write`   — создание/изменение отчётов
        - `analytics.report.run`     — запуск генерации/экспорта отчётов
        - `analytics.report.schedule`— управление scheduled-отчётами
        - `analytics.admin`          — управление кастомными шаблонами, default
    """

    @abstractmethod
    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        """Проверить наличие разрешения."""

    @abstractmethod
    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        """Проверить разрешение; выбросить
        ``InsufficientAnalyticsPermissionsException`` при отсутствии."""
