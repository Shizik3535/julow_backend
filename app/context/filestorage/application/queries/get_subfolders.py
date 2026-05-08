from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.folder_dto import FolderListDTO
from app.context.filestorage.application.dto.mappers import folder_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import FolderNotFoundException
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


class GetSubfoldersQuery(BaseQuery):
    """Запрос подпапок указанной папки."""

    parent_folder_id: str
    caller_id: str


class GetSubfoldersHandler(BaseQueryHandler[GetSubfoldersQuery, FolderListDTO]):
    """Подпапки папки."""

    REQUIRED_PERMISSION = "files.read"

    def __init__(
        self,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._folder_repo = folder_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetSubfoldersQuery) -> FolderListDTO:
        parent_id = Id.from_string(query.parent_folder_id)
        parent = await self._folder_repo.get_by_id(parent_id)
        if parent is None:
            raise FolderNotFoundException(id=query.parent_folder_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(parent.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        folders = await self._folder_repo.get_by_parent(parent_id)
        items = [folder_to_dto(f) for f in folders]
        return FolderListDTO(items=items, total=len(items))
