from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileListDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import FolderNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus


class GetFilesByFolderQuery(BaseQuery):
    """Запрос списка файлов в папке."""

    folder_id: str
    caller_id: str


class GetFilesByFolderHandler(BaseQueryHandler[GetFilesByFolderQuery, FileListDTO]):
    """Список файлов папки."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._folder_repo = folder_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetFilesByFolderQuery) -> FileListDTO:
        folder_id = Id.from_string(query.folder_id)
        folder = await self._folder_repo.get_by_id(folder_id)
        if folder is None:
            raise FolderNotFoundException(id=query.folder_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(folder.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        files = await self._file_repo.get_by_folder(folder_id)
        active = [f for f in files if f.status == FileStatus.ACTIVE]
        items = [file_to_dto(f) for f in active]
        return FileListDTO(items=items, total=len(items))
