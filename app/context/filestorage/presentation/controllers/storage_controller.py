from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import SuccessResponse

from app.context.filestorage.application.commands.create_storage import (
    CreateStorageCommand,
    CreateStorageHandler,
)
from app.context.filestorage.application.commands.update_storage import (
    SetStorageAllowedFileTypesCommand,
    SetStorageAllowedFileTypesHandler,
    SetStorageMaxFileSizeCommand,
    SetStorageMaxFileSizeHandler,
    UpdateStorageConfigCommand,
    UpdateStorageConfigHandler,
    UpdateStorageQuotaCommand,
    UpdateStorageQuotaHandler,
)
from app.context.filestorage.application.queries.get_storage import (
    GetStorageHandler,
    GetStorageQuery,
)
from app.context.filestorage.application.queries.get_storage_by_owner import (
    GetStorageByOwnerHandler,
    GetStorageByOwnerQuery,
)
from app.context.filestorage.presentation.dependencies import (
    get_current_user_id,
    get_filestorage_event_bus,
    get_fs_workspace_permission_checker,
    get_storage_repository,
)
from app.context.filestorage.presentation.schemas.requests.storage_requests import (
    CreateStorageRequest,
    SetAllowedFileTypesRequest,
    SetMaxFileSizeRequest,
    UpdateStorageConfigRequest,
    UpdateStorageQuotaRequest,
)
from app.context.filestorage.presentation.schemas.responses.storage_response import (
    StorageResponse,
)


class StorageController(BaseController):
    """
    Контроллер хранилища (FileStorage BC).

    Endpoint'ы (REST, префикс ``/fs/storages``):
        POST   /fs/storages                              — создать хранилище
        GET    /fs/storages/{id}                         — получить хранилище
        GET    /fs/storages/by-owner                     — получить по владельцу
        PATCH  /fs/storages/{id}/config                  — обновить конфигурацию
        PATCH  /fs/storages/{id}/quota                   — обновить квоту
        PUT    /fs/storages/{id}/allowed-file-types      — задать разрешённые типы
        PUT    /fs/storages/{id}/max-file-size           — задать макс. размер файла
    """

    def __init__(self) -> None:
        super().__init__(prefix="/fs/storages", tags=["FileStorage — Storages"])

    def _register_routes(self) -> None:
        self._router.add_api_route("/", self.create, methods=["POST"], status_code=201,
            response_model=SuccessResponse[StorageResponse], summary="Создать хранилище")
        self._router.add_api_route("/by-owner", self.get_by_owner, methods=["GET"],
            response_model=SuccessResponse[StorageResponse], summary="Получить по владельцу")
        self._router.add_api_route("/{storage_id}", self.get_storage, methods=["GET"],
            response_model=SuccessResponse[StorageResponse], summary="Получить хранилище")
        self._router.add_api_route("/{storage_id}/config", self.update_config, methods=["PATCH"],
            response_model=SuccessResponse[StorageResponse], summary="Обновить конфигурацию")
        self._router.add_api_route("/{storage_id}/quota", self.update_quota, methods=["PATCH"],
            response_model=SuccessResponse[StorageResponse], summary="Обновить квоту")
        self._router.add_api_route("/{storage_id}/allowed-file-types", self.set_allowed_types, methods=["PUT"],
            response_model=SuccessResponse[StorageResponse], summary="Разрешённые типы")
        self._router.add_api_route("/{storage_id}/max-file-size", self.set_max_file_size, methods=["PUT"],
            response_model=SuccessResponse[StorageResponse], summary="Макс. размер файла")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def create(
        self, body: CreateStorageRequest,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[StorageResponse]:
        handler = CreateStorageHandler(
            storage_repo=storage_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(CreateStorageCommand(
            caller_id=user_id, owner_type=body.owner_type, owner_id=body.owner_id,
            provider=body.provider, max_bytes=body.max_bytes,
            endpoint=body.endpoint, bucket=body.bucket, region=body.region,
            access_key_ref=body.access_key_ref, secret_key_ref=body.secret_key_ref,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def get_storage(
        self, storage_id: str,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[StorageResponse]:
        handler = GetStorageHandler(storage_repo=storage_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetStorageQuery(storage_id=storage_id, caller_id=user_id))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def get_by_owner(
        self,
        owner_type: str = Query(...),
        owner_id: str = Query(...),
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[StorageResponse]:
        handler = GetStorageByOwnerHandler(storage_repo=storage_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetStorageByOwnerQuery(
            owner_type=owner_type, owner_id=owner_id, caller_id=user_id,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def update_config(
        self, storage_id: str, body: UpdateStorageConfigRequest,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[StorageResponse]:
        handler = UpdateStorageConfigHandler(
            storage_repo=storage_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(UpdateStorageConfigCommand(
            caller_id=user_id, storage_id=storage_id,
            endpoint=body.endpoint, bucket=body.bucket, region=body.region,
            access_key_ref=body.access_key_ref, secret_key_ref=body.secret_key_ref,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def update_quota(
        self, storage_id: str, body: UpdateStorageQuotaRequest,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[StorageResponse]:
        handler = UpdateStorageQuotaHandler(
            storage_repo=storage_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(UpdateStorageQuotaCommand(
            caller_id=user_id, storage_id=storage_id, max_bytes=body.max_bytes,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def set_allowed_types(
        self, storage_id: str, body: SetAllowedFileTypesRequest,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[StorageResponse]:
        handler = SetStorageAllowedFileTypesHandler(
            storage_repo=storage_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(SetStorageAllowedFileTypesCommand(
            caller_id=user_id, storage_id=storage_id, file_types=body.file_types,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))

    async def set_max_file_size(
        self, storage_id: str, body: SetMaxFileSizeRequest,
        user_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[StorageResponse]:
        handler = SetStorageMaxFileSizeHandler(
            storage_repo=storage_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(SetStorageMaxFileSizeCommand(
            caller_id=user_id, storage_id=storage_id,
            max_file_size_bytes=body.max_file_size_bytes,
        ))
        return SuccessResponse(data=StorageResponse.model_validate(dto.model_dump()))
