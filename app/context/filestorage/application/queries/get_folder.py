from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.folder_dto import FolderDTO
from app.context.filestorage.application.dto.mappers import folder_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import FolderNotFoundException
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


class GetFolderQuery(BaseQuery):
    """Запрос папки по ID."""

    folder_id: str
    caller_id: str


class GetFolderHandler(BaseQueryHandler[GetFolderQuery, FolderDTO]):
    """Получение папки."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._folder_repo = folder_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetFolderQuery) -> FolderDTO:
        folder = await self._folder_repo.get_by_id(Id.from_string(query.folder_id))
        if folder is None:
            raise FolderNotFoundException(id=query.folder_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(folder.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return folder_to_dto(folder)
