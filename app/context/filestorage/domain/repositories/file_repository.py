from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.value_objects.file_type import FileType


class FileRepository(RepositoryPort[File]):
    """Порт репозитория для агрегата File."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[File]:
        """Найти файлы workspace."""

    @abstractmethod
    async def get_by_folder(self, folder_id: Id) -> list[File]:
        """Найти файлы в папке."""

    @abstractmethod
    async def get_by_uploader(self, uploader_id: Id) -> list[File]:
        """Найти файлы по загрузившему."""

    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[File]:
        """Найти файлы по владельцу."""

    @abstractmethod
    async def get_trashed_by_workspace(self, workspace_id: Id) -> list[File]:
        """Найти файлы в корзине workspace."""

    @abstractmethod
    async def search_by_name(self, query: str, workspace_id: Id) -> list[File]:
        """Поиск файлов по имени."""

    @abstractmethod
    async def get_by_tag(self, tag_name: str, workspace_id: Id) -> list[File]:
        """Найти файлы по тегу."""

    @abstractmethod
    async def get_by_type(self, file_type: FileType, workspace_id: Id) -> list[File]:
        """Найти файлы по типу."""

    @abstractmethod
    async def count_by_workspace(self, workspace_id: Id) -> int:
        """Подсчитать файлы в workspace."""

    @abstractmethod
    async def sum_size_by_workspace(self, workspace_id: Id) -> int:
        """Общий размер файлов в workspace."""
