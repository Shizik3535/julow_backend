from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository


class GetFileQuery(BaseQuery):
    """Запрос файла по ID."""

    file_id: str
    caller_id: str


class GetFileHandler(BaseQueryHandler[GetFileQuery, FileDTO]):
    """Получение файла. Требует `files.read`."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetFileQuery) -> FileDTO:
        file = await self._file_repo.get_by_id(Id.from_string(query.file_id))
        if file is None:
            raise FileNotFoundException(id=query.file_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return file_to_dto(file)
