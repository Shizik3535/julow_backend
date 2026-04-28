from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.project.application.dto.project_member_dto import ProjectMemberDTO


class ProjectMembershipProvider(ABC):
    """
    Outboard-порт: предоставление данных участников проекта другим BC.

    Реализуется в infrastructure слое Project BC.
    Task BC и другие инжектируют inboard-порт для проверки
    участия пользователя в проекте.
    """

    @abstractmethod
    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь участником проекта."""

    @abstractmethod
    async def get_member(self, project_id: str, user_id: str) -> ProjectMemberDTO | None:
        """Получить участника проекта."""

    @abstractmethod
    async def get_member_role(self, project_id: str, user_id: str) -> str | None:
        """
        Получить ID роли пользователя в проекте.

        Аргументы:
            project_id: Идентификатор проекта.
            user_id: Идентификатор пользователя.

        Возвращает:
            ID роли или None, если пользователь не состоит в проекте.
        """

    @abstractmethod
    async def get_project_member_ids(self, project_id: str) -> list[str]:
        """
        Получить список user_id всех активных участников проекта.

        Аргументы:
            project_id: Идентификатор проекта.

        Возвращает:
            Список user_id активных участников.
        """
