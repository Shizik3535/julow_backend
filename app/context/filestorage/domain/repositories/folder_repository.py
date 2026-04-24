from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.value_objects.folder_type import FolderType


class FolderRepository(RepositoryPort[Folder]):
    """Порт репозитория для агрегата Folder."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Folder]:
        """Найти папки workspace."""

    @abstractmethod
    async def get_by_parent(self, parent_folder_id: Id) -> list[Folder]:
        """Найти подпапки."""

    @abstractmethod
    async def get_root_folders(self, workspace_id: Id) -> list[Folder]:
        """Найти корневые папки workspace."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> Folder | None:
        """Найти папку проекта."""

    @abstractmethod
    async def get_by_type(self, folder_type: FolderType, workspace_id: Id) -> list[Folder]:
        """Найти папки по типу."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Folder]:
        """Поиск папок."""
