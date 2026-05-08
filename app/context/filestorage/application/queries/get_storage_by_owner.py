from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.mappers import storage_to_dto
from app.context.filestorage.application.dto.storage_dto import StorageDTO
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.storage_exceptions import StorageNotFoundException
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType


class GetStorageByOwnerQuery(BaseQuery):
    """Запрос хранилища по владельцу (workspace/organization)."""

    owner_type: str
    owner_id: str
    caller_id: str


class GetStorageByOwnerHandler(BaseQueryHandler[GetStorageByOwnerQuery, StorageDTO]):
    """Получение хранилища по владельцу."""

    REQUIRED_PERMISSION = "storage.read"

    def __init__(
        self,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetStorageByOwnerQuery) -> StorageDTO:
        owner_type = StorageOwnerType(query.owner_type)
        if owner_type == StorageOwnerType.WORKSPACE:
            await self._permission_checker.require_permission(
                user_id=query.caller_id,
                workspace_id=query.owner_id,
                permission=self.REQUIRED_PERMISSION,
            )
        storage = await self._storage_repo.get_by_owner(
            owner_type=owner_type, owner_id=Id.from_string(query.owner_id)
        )
        if storage is None:
            raise StorageNotFoundException(id=query.owner_id)
        return storage_to_dto(storage)
