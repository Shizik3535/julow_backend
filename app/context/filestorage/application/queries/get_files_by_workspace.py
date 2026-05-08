from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileDTO, FileListDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus


class GetFilesByWorkspaceQuery(BaseQuery):
    """Запрос списка файлов workspace."""

    workspace_id: str
    caller_id: str


class GetFilesByWorkspaceHandler(BaseQueryHandler[GetFilesByWorkspaceQuery, FileListDTO]):
    """Список активных файлов workspace."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetFilesByWorkspaceQuery) -> FileListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        files = await self._file_repo.get_by_workspace(Id.from_string(query.workspace_id))
        active = [f for f in files if f.status == FileStatus.ACTIVE]
        items = [file_to_dto(f) for f in active]
        return FileListDTO(items=items, total=len(items))
