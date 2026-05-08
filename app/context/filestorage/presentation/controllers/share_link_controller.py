from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.filestorage.application.commands.manage_share_link import (
    AccessShareLinkCommand,
    AccessShareLinkHandler,
    CreateShareLinkCommand,
    CreateShareLinkHandler,
    RevokeShareLinkCommand,
    RevokeShareLinkHandler,
)
from app.context.filestorage.presentation.dependencies import (
    get_current_user_id,
    get_file_repository,
    get_filestorage_event_bus,
    get_fs_workspace_permission_checker,
    get_password_port,
)
from app.context.filestorage.presentation.schemas.requests.file_requests import (
    AccessShareLinkRequest,
    CreateShareLinkRequest,
)
from app.context.filestorage.presentation.schemas.responses.file_response import (
    PublicShareLinkResponse,
)


class ShareLinkController(BaseController):
    """
    Контроллер публичных ссылок на файлы (FileStorage BC).

    Endpoint'ы (REST):
        POST   /files/{file_id}/share-links             — создать публичную ссылку
        DELETE /files/{file_id}/share-links/{link_id}   — отозвать публичную ссылку
        POST   /share-links/access/{token}              — перейти по публичной ссылке (без авторизации)
    """

    def __init__(self) -> None:
        super().__init__(prefix="", tags=["FileStorage — Share Links"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/files/{file_id}/share-links",
            self.create_link,
            methods=["POST"],
            status_code=201,
            response_model=SuccessResponse[PublicShareLinkResponse],
            summary="Создать публичную ссылку",
        )
        self._router.add_api_route(
            "/files/{file_id}/share-links/{link_id}",
            self.revoke_link,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Отозвать публичную ссылку",
        )
        self._router.add_api_route(
            "/share-links/access/{token}",
            self.access_link,
            methods=["POST"],
            response_model=SuccessResponse[dict],
            summary="Перейти по публичной ссылке",
            description=(
                "Не требует авторизации. Возвращает метаданные файла "
                "и инкрементирует счётчик использований."
            ),
        )

    async def create_link(
        self, file_id: str, body: CreateShareLinkRequest,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        password_port=Depends(get_password_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[PublicShareLinkResponse]:
        handler = CreateShareLinkHandler(
            file_repo=file_repo, permission_checker=permission_checker,
            password_port=password_port, event_bus=event_bus,
        )
        dto = await handler.handle(CreateShareLinkCommand(
            caller_id=user_id, file_id=file_id,
            access_level=body.access_level, password=body.password,
            expires_at=body.expires_at, max_uses=body.max_uses,
        ))
        return SuccessResponse(data=PublicShareLinkResponse.model_validate(dto.model_dump()))

    async def revoke_link(
        self, file_id: str, link_id: str,
        user_id: str = Depends(get_current_user_id),
        file_repo=Depends(get_file_repository),
        permission_checker=Depends(get_fs_workspace_permission_checker),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> MessageResponse:
        handler = RevokeShareLinkHandler(
            file_repo=file_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RevokeShareLinkCommand(
            caller_id=user_id, file_id=file_id, link_id=link_id,
        ))
        return MessageResponse(data=MessageData(message="Публичная ссылка отозвана"))

    async def access_link(
        self, token: str, body: AccessShareLinkRequest | None = None,
        file_repo=Depends(get_file_repository),
        password_port=Depends(get_password_port),
        event_bus=Depends(get_filestorage_event_bus),
    ) -> SuccessResponse[dict]:
        handler = AccessShareLinkHandler(
            file_repo=file_repo, password_port=password_port, event_bus=event_bus,
        )
        result = await handler.handle(AccessShareLinkCommand(
            token=token, password=body.password if body else None,
        ))
        return SuccessResponse(data=result)
