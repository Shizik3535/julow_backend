from __future__ import annotations

from abc import ABC, abstractmethod


class TimeTrackingPermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте TimeTracking BC.

    TimeTracking BC не содержит собственного агрегата ролей. Проверка
    делегируется в Workspace BC (`WorkspaceMembershipProvider.has_permission`),
    который инкапсулирует каскад WorkspaceRole → OrgRole.

    Используемое permission-пространство (workspace-уровень):
        - `time.read`     — чтение записей времени
        - `time.write`    — создание/редактирование своих записей
        - `time.delete`   — удаление своих записей
        - `time.submit`   — отправка на утверждение
        - `time.approve`  — утверждение/отклонение чужих записей
        - `time.admin`    — управление категориями, тегами, lock-периода
    """

    @abstractmethod
    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        """Проверить наличие разрешения."""

    @abstractmethod
    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        """Проверить разрешение; выбросить
        ``InsufficientTimeTrackingPermissionsException`` при отсутствии."""
