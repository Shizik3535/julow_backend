from __future__ import annotations

from urllib.parse import quote

from fastapi import Depends, File, Form, Query, UploadFile
from fastapi.responses import Response

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.filestorage.application.commands.add_file_version import (
    AddFileVersionCommand,
    AddFileVersionHandler,
)
from app.context.filestorage.application.commands.lifecycle_file import (
    DeleteFileCommand,
    DeleteFileHandler,
    RestoreFileCommand,
    RestoreFileHandler,
    TrashFileCommand,
    TrashFileHandler,
)
from app.context.filestorage.application.commands.lock_file import (
    LockFileCommand,
    LockFileHandler,
    UnlockFileCommand,
    UnlockFileHandler,
)
from app.context.filestorage.application.commands.manage_file_permission import (
    GrantFilePermissionCommand,
    GrantFilePermissionHandler,
    RevokeFilePermissionCommand,
    RevokeFilePermissionHandler,
)
from app.context.filestorage.application.commands.manage_file_tag import (
    AddFileTagCommand,
    AddFileTagHandler,
    RemoveFileTagCommand,
    RemoveFileTagHandler,
)
from app.context.filestorage.application.commands.update_file import (
    MoveFileCommand,
    MoveFileHandler,
    RenameFileCommand,
    RenameFileHandler,
    UpdateFileDescriptionCommand,
    UpdateFileDescriptionHandler,
)
from app.context.filestorage.application.commands.upload_file import (
    UploadFileCommand,
    UploadFileHandler,
)
from app.context.filestorage.application.queries.get_file import (
    GetFileHandler,
    GetFileQuery,
)
from app.context.filestorage.application.queries.get_file_content import (
    GetFileContentHandler,
    GetFileContentQuery,
)
from app.context.filestorage.application.queries.get_file_download_url import (
    GetFileDownloadUrlHandler,
    GetFileDownloadUrlQuery,
)
from app.context.filestorage.application.queries.get_files_by_folder import (
    GetFilesByFolderHandler,
    GetFilesByFolderQuery,
)
from app.context.filestorage.application.queries.get_files_by_workspace import (
    GetFilesByWorkspaceHandler,
    GetFilesByWorkspaceQuery,
)
from app.context.filestorage.application.queries.get_trashed_files import (
    GetTrashedFilesHandler,
    GetTrashedFilesQuery,
)
from app.context.filestorage.application.queries.search_files import (
    SearchFilesHandler,
    SearchFilesQuery,
)
from app.context.filestorage.presentation.dependencies import (
    get_block_pending_downloads,
    get_current_user_id,
    get_file_repository,
    get_file_storage_port,
    get_filestorage_event_bus,
    get_folder_repository,
    get_fs_identity_user_port,
    get_fs_workspace_permission_checker,
    get_storage_repository,
)
from app.context.filestorage.presentation.schemas.requests.file_requests import (
    AddFileTagRequest,
    GrantFilePermissionRequest,
    LockFileRequest,
    MoveFileRequest,
    RenameFileRequest,
    UpdateFileDescriptionRequest,
)
from app.context.filestorage.presentation.schemas.responses.file_response import (
    FileDownloadUrlResponse,
    FileListResponse,
    FileResponse,
)


class FileController(BaseController):
    """
    Контроллер файлов (FileStorage BC).

    Endpoint'ы (REST, префикс ``/files``):
        POST   /files                                  — загрузить файл (multipart)
        GET    /files                                  — поиск/список файлов workspace
        GET    /files/trashed                          — файлы в корзине workspace
        GET    /files/{id}                             — получить файл
        GET    /files/{id}/download                    — получить presigned URL
        GET    /files/{id}/content                     — стримить содержимое файла
        PATCH  /files/{id}/rename                      — переименовать
        POST   /files/{id}/move                        — переместить
        PATCH  /files/{id}/description                 — обновить описание
        POST   /files/{id}/trash                       — в корзину
        POST   /files/{id}/restore                     — из корзины
        DELETE /files/{id}                             — окончательно удалить
        POST   /files/{id}/versions                    — добавить версию
        POST   /files/{id}/permissions                 — выдать разрешение
        DELETE /files/{id}/permissions                 — отозвать разрешение
        POST   /files/{id}/lock                        — заблокировать
        POST   /files/{id}/unlock                      — разблокировать
        POST   /files/{id}/tags                        — добавить тег
        DELETE /files/{id}/tags/{tag_name}             — удалить тег
        GET    /folders/{id}/files                     — файлы в папке
    """

    def __init__(self) -> None:
        super().__init__(prefix="/files", tags=["FileStorage — Files"])

    def _register_routes(self) -> None:
        self._router.add_api_route("/", self.upload_file, methods=["POST"], status_code=201,
            response_model=SuccessResponse[FileResponse], summary="Загрузить файл",
            responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
        self._router.add_api_route("/", self.search_files, methods=["GET"],
            response_model=SuccessResponse[FileListResponse], summary="Поиск/список файлов")
        self._router.add_api_route("/trashed", self.list_trashed, methods=["GET"],
            response_model=SuccessResponse[FileListResponse], summary="Файлы в корзине")
        self._router.add_api_route("/{file_id}", self.get_file, methods=["GET"],
            response_model=SuccessResponse[FileResponse], summary="Получить файл")
        self._router.add_api_route("/{file_id}/download", self.get_download_url, methods=["GET"],
            response_model=SuccessResponse[FileDownloadUrlResponse], summary="Presigned URL")
        self._router.add_api_route("/{file_id}/content", self.get_content, methods=["GET"],
            summary="Сырое содержимое файла (bytes)",
            responses={
                200: {"content": {"application/octet-stream": {}}},
                401: {"model": ErrorResponse},
                403: {"model": ErrorResponse},
                404: {"model": ErrorResponse},
            })
        self._router.add_api_route("/{file_id}/rename", self.rename, methods=["PATCH"],
            response_model=SuccessResponse[FileResponse], summary="Переименовать")
        self._router.add_api_route("/{file_id}/move", self.move, methods=["POST"],
            response_model=SuccessResponse[FileResponse], summary="Переместить в папку")
        self._router.add_api_route("/{file_id}/description", self.update_description, methods=["PATCH"],
            response_model=SuccessResponse[FileResponse], summary="Обновить описание")
        self._router.add_api_route("/{file_id}/trash", self.trash, methods=["POST"],
            response_model=MessageResponse, summary="В корзину")
        self._router.add_api_route("/{file_id}/restore", self.restore, methods=["POST"],
            response_model=MessageResponse, summary="Восстановить из корзины")
        self._router.add_api_route("/{file_id}", self.delete, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить окончательно")
        self._router.add_api_route("/{file_id}/versions", self.add_version, methods=["POST"], status_code=201,
            response_model=SuccessResponse[FileResponse], summary="Добавить версию")
        self._router.add_api_route("/{file_id}/permissions", self.grant_permission, methods=["POST"],
            response_model=MessageResponse, summary="Выдать разрешение")
        self._router.add_api_route("/{file_id}/permissions", self.revoke_permission, methods=["DELETE"],
            response_model=MessageResponse, summary="Отозвать разрешение")
        self._router.add_api_route("/{file_id}/lock", self.lock, methods=["POST"],
            response_model=MessageResponse, summary="Заблокировать")
        self._router.add_api_route("/{file_id}/unlock", self.unlock, methods=["POST"],
            response_model=MessageResponse, summary="Разблокировать")
        self._router.add_api_route("/{file_id}/tags", self.add_tag, methods=["POST"],
            response_model=MessageResponse, summary="Добавить тег")
        self._router.add_api_route("/{file_id}/tags/{tag_name}", self.remove_tag, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить тег")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def upload_file(
        self,
        workspace_id: str = Form(...),
        file: UploadFile = File(...),
        folder_id: str | None = Form(default=None),
        description: str | None = Form(default=None),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        folder_repo=Depends(get_folder_repository),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FileResponse]:
        data = await file.read()
        handler = UploadFileHandler(
            file_repo=file_repo,
            folder_repo=folder_repo,
            storage_repo=storage_repo,
            permission_checker=permission_checker,
            file_storage=file_storage,
            event_bus=event_bus,
        )
        dto = await handler.handle(
            UploadFileCommand(
                caller_id=user_id,
                workspace_id=workspace_id,
                filename=file.filename or "unnamed",
                content_type=file.content_type or "application/octet-stream",
                file_data=data,
                folder_id=folder_id,
                description=description,
            )
        )
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def search_files(
        self,
        workspace_id: str = Query(...),
        query: str | None = Query(default=None),
        file_type: str | None = Query(default=None),
        tag: str | None = Query(default=None),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FileListResponse]:
        if query or file_type or tag:
            handler = SearchFilesHandler(file_repo=file_repo, permission_checker=permission_checker)
            dto = await handler.handle(SearchFilesQuery(
                workspace_id=workspace_id, caller_id=user_id,
                query=query, file_type=file_type, tag=tag,
            ))
        else:
            handler = GetFilesByWorkspaceHandler(file_repo=file_repo, permission_checker=permission_checker)
            dto = await handler.handle(GetFilesByWorkspaceQuery(
                workspace_id=workspace_id, caller_id=user_id,
            ))
        return SuccessResponse(data=FileListResponse.model_validate(dto.model_dump()))

    async def list_trashed(
        self,
        workspace_id: str = Query(...),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FileListResponse]:
        handler = GetTrashedFilesHandler(file_repo=file_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetTrashedFilesQuery(
            workspace_id=workspace_id, caller_id=user_id,
        ))
        return SuccessResponse(data=FileListResponse.model_validate(dto.model_dump()))

    async def get_file(
        self,
        file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
    ) -> SuccessResponse[FileResponse]:
        handler = GetFileHandler(file_repo=file_repo, permission_checker=permission_checker)
        dto = await handler.handle(GetFileQuery(file_id=file_id, caller_id=user_id))
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def get_download_url(
        self,
        file_id: str,
        expires_in: int = Query(default=3600, ge=60, le=86400),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_filestorage_event_bus),
        block_pending_downloads: bool = Depends(get_block_pending_downloads),
    ) -> SuccessResponse[FileDownloadUrlResponse]:
        handler = GetFileDownloadUrlHandler(
            file_repo=file_repo, permission_checker=permission_checker,
            file_storage=file_storage, event_bus=event_bus,
            block_pending_downloads=block_pending_downloads,
        )
        result = await handler.handle(GetFileDownloadUrlQuery(
            file_id=file_id, caller_id=user_id, expires_in=expires_in,
        ))
        return SuccessResponse(data=FileDownloadUrlResponse.model_validate(result))

    async def get_content(
        self,
        file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_filestorage_event_bus),
        block_pending_downloads: bool = Depends(get_block_pending_downloads),
    ) -> Response:
        """Стримить сырое содержимое файла через API.

        Используется клиентами, у которых нет сетевого доступа к S3/MinIO
        напрямую (например, мобильные приложения за NAT, или web-фронтенд,
        ходящий через server-side proxy с Bearer-токеном). Возвращает
        ``application/octet-stream`` с заголовком ``Content-Disposition: inline``,
        чтобы браузеры умели открывать картинки/видео прямо в `<img>`/`<video>`.
        """
        handler = GetFileContentHandler(
            file_repo=file_repo, permission_checker=permission_checker,
            file_storage=file_storage, event_bus=event_bus,
            block_pending_downloads=block_pending_downloads,
        )
        result = await handler.handle(GetFileContentQuery(
            file_id=file_id, caller_id=user_id,
        ))
        # RFC 5987 — кодируем имя файла, чтобы кириллица/пробелы не ломали заголовок.
        encoded_name = quote(result.name, safe="")
        return Response(
            content=result.data,
            media_type=result.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": (
                    f'inline; filename="{encoded_name}"; '
                    f"filename*=UTF-8''{encoded_name}"
                ),
                "Content-Length": str(result.size_bytes),
                # Кэшируем приватно на короткое время — содержимое файла иммутабельно
                # для одного storage_path; обновление файла создаёт новую версию.
                "Cache-Control": "private, max-age=300",
            },
        )

    async def rename(
        self, file_id: str, body: RenameFileRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FileResponse]:
        handler = RenameFileHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        dto = await handler.handle(RenameFileCommand(
            caller_id=user_id, file_id=file_id, new_name=body.new_name,
        ))
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def move(
        self, file_id: str, body: MoveFileRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        folder_repo=Depends(get_folder_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FileResponse]:
        handler = MoveFileHandler(
            file_repo=file_repo, folder_repo=folder_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        dto = await handler.handle(MoveFileCommand(
            caller_id=user_id, file_id=file_id, new_folder_id=body.new_folder_id,
        ))
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def update_description(
        self, file_id: str, body: UpdateFileDescriptionRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FileResponse]:
        handler = UpdateFileDescriptionHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        dto = await handler.handle(UpdateFileDescriptionCommand(
            caller_id=user_id, file_id=file_id, description=body.description,
        ))
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def trash(
        self, file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = TrashFileHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(TrashFileCommand(caller_id=user_id, file_id=file_id))
        return MessageResponse(data=MessageData(message="Файл перемещён в корзину"))

    async def restore(
        self, file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = RestoreFileHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(RestoreFileCommand(caller_id=user_id, file_id=file_id))
        return MessageResponse(data=MessageData(message="Файл восстановлен"))

    async def delete(
        self, file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = DeleteFileHandler(
            file_repo=file_repo, storage_repo=storage_repo,
            permission_checker=permission_checker, file_storage=file_storage,
            event_bus=event_bus,
        )
        await handler.handle(DeleteFileCommand(caller_id=user_id, file_id=file_id))
        return MessageResponse(data=MessageData(message="Файл удалён"))

    async def add_version(
        self, file_id: str,
        file: UploadFile = File(...),
        change_summary: str | None = Form(default=None),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        storage_repo=Depends(get_storage_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[FileResponse]:
        data = await file.read()
        handler = AddFileVersionHandler(
            file_repo=file_repo, storage_repo=storage_repo,
            permission_checker=permission_checker, file_storage=file_storage,
            event_bus=event_bus,
        )
        dto = await handler.handle(AddFileVersionCommand(
            caller_id=user_id, file_id=file_id,
            file_data=data,
            content_type=file.content_type or "application/octet-stream",
            change_summary=change_summary,
        ))
        return SuccessResponse(data=FileResponse.model_validate(dto.model_dump()))

    async def grant_permission(
        self, file_id: str, body: GrantFilePermissionRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        identity_port=Depends(get_fs_identity_user_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = GrantFilePermissionHandler(
            file_repo=file_repo, permission_checker=permission_checker,
            identity_port=identity_port, event_bus=event_bus,
        )
        await handler.handle(GrantFilePermissionCommand(
            caller_id=user_id, file_id=file_id,
            user_id=body.user_id, team_id=body.team_id,
            access_level=body.access_level,
        ))
        return MessageResponse(data=MessageData(message="Разрешение выдано"))

    async def revoke_permission(
        self, file_id: str,
        target_user_id: str | None = Query(default=None, alias="user_id"),
        target_team_id: str | None = Query(default=None, alias="team_id"),
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = RevokeFilePermissionHandler(
            file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RevokeFilePermissionCommand(
            caller_id=user_id, file_id=file_id,
            user_id=target_user_id, team_id=target_team_id,
        ))
        return MessageResponse(data=MessageData(message="Разрешение отозвано"))

    async def lock(
        self, file_id: str, body: LockFileRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = LockFileHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(LockFileCommand(
            caller_id=user_id, file_id=file_id,
            reason=body.reason, expires_at=body.expires_at,
        ))
        return MessageResponse(data=MessageData(message="Файл заблокирован"))

    async def unlock(
        self, file_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = UnlockFileHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(UnlockFileCommand(caller_id=user_id, file_id=file_id))
        return MessageResponse(data=MessageData(message="Файл разблокирован"))

    async def add_tag(
        self, file_id: str, body: AddFileTagRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = AddFileTagHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(AddFileTagCommand(
            caller_id=user_id, file_id=file_id, tag_name=body.tag_name, color=body.color,
        ))
        return MessageResponse(data=MessageData(message="Тег добавлен"))

    async def remove_tag(
        self, file_id: str, tag_name: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = RemoveFileTagHandler(file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus)
        await handler.handle(RemoveFileTagCommand(
            caller_id=user_id, file_id=file_id, tag_name=tag_name,
        ))
        return MessageResponse(data=MessageData(message="Тег удалён"))
