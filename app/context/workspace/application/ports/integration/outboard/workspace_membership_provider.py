from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.workspace.application.dto.workspace_member_dto import WorkspaceMemberDTO


class WorkspaceMembershipProvider(ABC):
    """
    Outbound-порт: предоставление данных членства в workspace другим BC.

    Реализуется в infrastructure слое Workspace BC.
    Другие BC инжектируют соответствующий inboard-порт,
    адаптер которого делегирует в этот provider.
    """

    @abstractmethod
    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь участником workspace."""

    @abstractmethod
    async def get_member_role(self, workspace_id: str, user_id: str) -> str | None:
        """Получить роль участника workspace (None — не участник)."""

    @abstractmethod
    async def get_members(self, workspace_id: str) -> list[WorkspaceMemberDTO]:
        """Получить всех участников workspace."""

    @abstractmethod
    async def has_permission(self, workspace_id: str, user_id: str, permission: str) -> bool:
        """
        Проверить, есть ли у пользователя разрешение в workspace.

        Учитывает как workspace-роль (прямой участник), так и каскад
        орг-роли, если workspace принадлежит организации.

        Аргументы:
            workspace_id: Идентификатор workspace.
            user_id: Идентификатор пользователя.
            permission: Требуемое разрешение (например «members.read»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """
