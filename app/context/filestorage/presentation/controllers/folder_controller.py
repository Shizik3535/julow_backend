from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.filestorage.application.commands.create_folder import (
    CreateFolderCommand,
    CreateFolderHandler,
)
from app.context.filestorage.application.commands.delete_folder import (
    DeleteFolderCommand,
    DeleteFolderHandler,
)
from app.context.filestorage.application.commands.update_folder import (
    MoveFolderCommand,
    MoveFolderHandler,
    PinFolderCommand,
    PinFolderHandler,
    RenameFolderCommand,
    RenameFolderHandler,
    UnpinFolderCommand,
    UnpinFolderHandler,
    UpdateFolderDescriptionCommand,
    UpdateFolderDescriptionHandler,
)
from app.context.filestorage.application.queries.get_files_by_folder import (
    GetFilesByFolderHandler,
    GetFilesByFolderQuery,
)
from app.context.filestorage.application.queries.get_folder import (
    GetFolderHandler,
    GetFolderQuery,
)
from app.context.filestorage.application.queries.get_folders_by_workspace import (
    GetFoldersByWorkspaceHandler,
    GetFoldersByWorkspaceQuery,
)
from app.context.filestorage.application.queries.get_subfolders import (
    GetSubfoldersHandler,
    GetSubfoldersQuery,
)
from app.context.filestorage.presentation.dependencies import (
    get_current_user_id,
    get_file_repository,
    get_filestorage_event_bus,
    get_folder_repository,
    get_fs_workspace_permission_checker,
)
from app.context.filestorage.presentation.schemas.requests.folder_requests import (
    CreateFolderRequest,
    MoveFolderRequest,
    RenameFolderRequest,
    UpdateFolderDescriptionRequest,
)
from app.context.filestorage.presentation.schemas.responses.file_response import FileListResponse
from app.context.filestorage.presentation.schemas.responses.folder_response import (
    FolderListResponse,
    FolderResponse,
)


class FolderController(BaseController):
    """
    Контроллер папок (FileStorage BC).

    Endpoint'ы (REST, префикс ``/folders``):
        POST   /folders                                 — создать папку
        GET    /folders                                 — список корневых папок workspace
        GET    /folders/{id}                            — получить папку
        GET    /folders/{id}/subfolders                 — подпапки
        GET    /folders/{id}/files                      — файлы в папке
        PATCH  /folders/{id}/rename                     — переименовать
        POST   /folders/{id}/move                       — переместить
        PATCH  /folders/{id}/description                — обновить описание
        POST   /folders/{id}/pin                        — закрепить
        POST   /folders/{id}/unpin                      — открепить
        DELETE /folders/{id}                            — удалить (только пустую)
    """

    def __init__(self) -> None:
        super().__init__(prefix="/folders", tags=["FileStorage — Folders"])

    def _register_routes(self) -> None:
        self._router.add_api_route("/", self.create, methods=["POST"], status_code=201,
            response_model=SuccessResponse[FolderResponse], summary="Создать папку")
        self._router.add_api_route("/", self.list_folders, methods=["GET"],
            response_model=SuccessResponse[FolderListResponse], summary="Список папок workspace")
        self._router.add_api_route("/{folder_id}", self.get_folder, methods=["GET"],
            response_model=SuccessResponse[FolderResponse], summary="Получить папку")
        self._router.add_api_route("/{folder_id}/subfolders", self.list_subfolders, methods=["GET"],
            response_model=SuccessResponse[FolderListResponse], summary="Подпапки")
        self._router.add_api_route("/{folder_id}/files", self.list_files, methods=["GET"],
            response_model=SuccessResponse[FileListResponse], summary="Файлы в папке")
        self._router.add_api_route("/{folder_id}/rename", self.rename, methods=["PATCH"],
            response_model=SuccessResponse[FolderResponse], summary="Переименовать")
        self._router.add_api_route("/{folder_id}/move", self.move, methods=["POST"],
            response_model=SuccessResponse[FolderResponse], summary="Переместить")
        self._router.add_api_route("/{folder_id}/description", self.update_description, methods=["PATCH"],
            response_model=SuccessResponse[FolderResponse], summary="Описание")
        self._router.add_api_route("/{folder_id}/pin", self.pin, methods=["POST"],
            response_model=MessageResponse, summary="Закрепить")
        self._router.add_api_route("/{folder_id}/unpin", self.unpin, methods=["POST"],
            response_model=MessageResponse, summary="Открепить")
        self._router.add_api_route("/{folder_id}", self.delete, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить (только пустую)")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def create(
        self, body: CreateFolderRequest,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FolderResponse]:
        handler = CreateFolderHandler(
            folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(CreateFolderCommand(
            caller_id=user_id, workspace_id=body.workspace_id, name=body.name,
            parent_folder_id=body.parent_folder_id, color=body.color,
            description=body.description, icon=body.icon,
        ))
        return SuccessResponse(data=FolderResponse.model_validate(dto.model_dump()))

    async def list_folders(
        self,
        workspace_id: str = Query(...),
        only_root: bool = Query(default=True),
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FolderListResponse]:
        handler = GetFoldersByWorkspaceHandler(folder_repo=folder_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetFoldersByWorkspaceQuery(
            workspace_id=workspace_id, caller_id=user_id, only_root=only_root,
        ))
        return SuccessResponse(data=FolderListResponse.model_validate(dto.model_dump()))

    async def get_folder(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FolderResponse]:
        handler = GetFolderHandler(folder_repo=folder_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetFolderQuery(folder_id=folder_id, caller_id=user_id))
        return SuccessResponse(data=FolderResponse.model_validate(dto.model_dump()))

    async def list_subfolders(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FolderListResponse]:
        handler = GetSubfoldersHandler(folder_repo=folder_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetSubfoldersQuery(parent_folder_id=folder_id, caller_id=user_id))
        return SuccessResponse(data=FolderListResponse.model_validate(dto.model_dump()))

    async def list_files(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FileListResponse]:
        handler = GetFilesByFolderHandler(
            file_repo=file_repo, folder_repo=folder_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetFilesByFolderQuery(folder_id=folder_id, caller_id=user_id))
        return SuccessResponse(data=FileListResponse.model_validate(dto.model_dump()))

    async def rename(
        self, folder_id: str, body: RenameFolderRequest,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FolderResponse]:
        handler = RenameFolderHandler(folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus)
        dto = await handler.handle(RenameFolderCommand(
            caller_id=user_id, folder_id=folder_id, new_name=body.new_name,
        ))
        return SuccessResponse(data=FolderResponse.model_validate(dto.model_dump()))

    async def move(
        self, folder_id: str, body: MoveFolderRequest,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FolderResponse]:
        handler = MoveFolderHandler(folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus)
        dto = await handler.handle(MoveFolderCommand(
            caller_id=user_id, folder_id=folder_id,
            new_parent_folder_id=body.new_parent_folder_id,
        ))
        return SuccessResponse(data=FolderResponse.model_validate(dto.model_dump()))

    async def update_description(
        self, folder_id: str, body: UpdateFolderDescriptionRequest,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FolderResponse]:
        handler = UpdateFolderDescriptionHandler(folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus)
        dto = await handler.handle(UpdateFolderDescriptionCommand(
            caller_id=user_id, folder_id=folder_id, description=body.description,
        ))
        return SuccessResponse(data=FolderResponse.model_validate(dto.model_dump()))

    async def pin(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = PinFolderHandler(folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(PinFolderCommand(caller_id=user_id, folder_id=folder_id))
        return MessageResponse(data=MessageData(message="Папка закреплена"))

    async def unpin(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = UnpinFolderHandler(folder_repo=folder_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(UnpinFolderCommand(caller_id=user_id, folder_id=folder_id))
        return MessageResponse(data=MessageData(message="Папка откреплена"))

    async def delete(
        self, folder_id: str,
        user_id: str = Depends(get_current_user_id),
        folder_repo=Depends(get_folder_repository),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = DeleteFolderHandler(
            folder_repo=folder_repo, file_repo=file_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(DeleteFolderCommand(caller_id=user_id, folder_id=folder_id))
        return MessageResponse(data=MessageData(message="Папка удалена"))
