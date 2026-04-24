from __future__ import annotations

from abc import ABC, abstractmethod


class ProjectPermissionProvider(ABC):
    """
    Outboard-порт: предоставление проверки разрешений проекта другим BC.

    Реализуется в infrastructure слое Project BC.
    Другие BC (Task BC и др.) инжектируют соответствующий inboard-порт,
    адаптер которого делегирует в этот provider.

    Provider инкапсулирует wildcard-логику и каскад
    ProjectRole → WorkspaceRole → OrgRole.
    """

    @abstractmethod
    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        """
        Проверить, есть ли у пользователя разрешение в проекте
        (с учётом каскада workspace/org).

        Аргументы:
            user_id: Идентификатор пользователя.
            project_id: Идентификатор проекта.
            permission: Требуемое project-разрешение (например «content.read»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """
