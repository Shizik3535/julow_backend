from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileListDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.file_type import FileType


class SearchFilesQuery(BaseQuery):
    """
    Запрос поиска файлов в workspace по имени и/или фильтрам.

    Атрибуты:
        workspace_id: ID workspace.
        caller_id: ID пользователя.
        query: Подстрока в имени файла (опционально).
        file_type: Фильтр по типу (опционально).
        tag: Фильтр по тегу (опционально).
    """

    workspace_id: str
    caller_id: str
    query: str | None = None
    file_type: str | None = None
    tag: str | None = None


class SearchFilesHandler(BaseQueryHandler[SearchFilesQuery, FileListDTO]):
    """Поиск файлов с фильтрами."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker

    async def handle(self, query: SearchFilesQuery) -> FileListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws_id = Id.from_string(query.workspace_id)
        if query.tag:
            files = await self._file_repo.get_by_tag(query.tag, ws_id)
        elif query.file_type:
            files = await self._file_repo.get_by_type(FileType(query.file_type), ws_id)
        elif query.query:
            files = await self._file_repo.search_by_name(query.query, ws_id)
        else:
            files = await self._file_repo.get_by_workspace(ws_id)
        files = [f for f in files if f.status == FileStatus.ACTIVE]
        items = [file_to_dto(f) for f in files]
        return FileListDTO(items=items, total=len(items))
