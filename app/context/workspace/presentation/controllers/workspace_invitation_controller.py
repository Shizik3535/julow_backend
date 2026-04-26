from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.commands.send_workspace_invitation import (
    SendWorkspaceInvitationCommand,
    SendWorkspaceInvitationHandler,
)
from app.context.workspace.application.commands.send_bulk_workspace_invitations import (
    SendBulkWorkspaceInvitationsCommand,
    SendBulkWorkspaceInvitationsHandler,
)
from app.context.workspace.application.commands.generate_workspace_invitation_link import (
    GenerateWorkspaceInvitationLinkCommand,
    GenerateWorkspaceInvitationLinkHandler,
)
from app.context.workspace.application.commands.revoke_workspace_invitation import (
    RevokeWorkspaceInvitationCommand,
    RevokeWorkspaceInvitationHandler,
)
from app.context.workspace.application.commands.accept_workspace_invitation import (
    AcceptWorkspaceInvitationCommand,
    AcceptWorkspaceInvitationHandler,
)
from app.context.workspace.application.commands.decline_workspace_invitation import (
    DeclineWorkspaceInvitationCommand,
    DeclineWorkspaceInvitationHandler,
)
from app.context.workspace.application.queries.get_workspace_invitations import (
    GetWorkspaceInvitationsHandler,
    GetWorkspaceInvitationsQuery,
)
from app.context.workspace.application.queries.get_workspace_invitation_by_token import (
    GetWorkspaceInvitationByTokenHandler,
    GetWorkspaceInvitationByTokenQuery,
)
from app.context.workspace.application.queries.search_my_workspace_invitations import (
    SearchMyWorkspaceInvitationsHandler,
    SearchMyWorkspaceInvitationsQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_event_bus,
    get_workspace_invitation_repository,
    get_workspace_membership_repository,
    get_workspace_permission_checker,
    get_workspace_repository,
    get_ws_identity_user_port,
)
from app.context.workspace.presentation.schemas.requests.generate_workspace_invitation_link_request import (
    GenerateWorkspaceInvitationLinkRequest,
)
from app.context.workspace.presentation.schemas.requests.send_bulk_workspace_invitations_request import (
    SendBulkWorkspaceInvitationsRequest,
)
from app.context.workspace.presentation.schemas.requests.send_workspace_invitation_request import (
    SendWorkspaceInvitationRequest,
)
from app.context.workspace.presentation.schemas.responses.workspace_invitation_response import WorkspaceInvitationResponse


class WorkspaceInvitationController(BaseController):
    """
    Контроллер приглашений в workspace.

    Endpoint'ы:
        GET    /{ws_id}/invitations                          — Список приглашений
        POST   /{ws_id}/invitations/email                    — Отправить email-приглашение
        POST   /{ws_id}/invitations/bulk                     — Массовая отправка
        POST   /{ws_id}/invitations/link                     — Сгенерировать ссылку
        POST   /{ws_id}/invitations/{invitation_id}/revoke   — Отозвать приглашение
        GET    /invitations/token/{token}                     — По токену ссылки
        POST   /invitations/{invitation_id}/accept            — Принять приглашение
        POST   /invitations/{invitation_id}/decline           — Отклонить приглашение
        GET    /invitations/mine                             — Мои приглашения
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces", tags=["Workspace / Invitations"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{ws_id}/invitations",
            self.get_invitations,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceInvitationResponse],
            summary="Список приглашений workspace",
            description="Возвращает пагинированный список приглашений workspace.",
            responses={
                200: {"description": "Список приглашений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/invitations/email",
            self.send_invitation,
            methods=["POST"],
            response_model=SuccessResponse[WorkspaceInvitationResponse],
            status_code=201,
            summary="Отправить email-приглашение",
            description="Отправляет приглашение в workspace по email.",
            responses={
                201: {"description": "Приглашение отправлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Приглашение уже отправлено", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/invitations/bulk",
            self.send_bulk_invitations,
            methods=["POST"],
            response_model=PaginatedResponse[WorkspaceInvitationResponse],
            status_code=201,
            summary="Массовая отправка приглашений",
            description="Отправляет приглашения в workspace по списку email-адресов.",
            responses={
                201: {"description": "Приглашения отправлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/invitations/link",
            self.generate_invitation_link,
            methods=["POST"],
            response_model=SuccessResponse[WorkspaceInvitationResponse],
            status_code=201,
            summary="Сгенерировать ссылку-приглашение",
            description="Генерирует ссылку-приглашение для входа в workspace.",
            responses={
                201: {"description": "Ссылка сгенерирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/invitations/{invitation_id}/revoke",
            self.revoke_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отозвать приглашение",
            description="Отзывает отправленное приглашение в workspace.",
            responses={
                200: {"description": "Приглашение отозвано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/token/{token}",
            self.get_invitation_by_token,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceInvitationResponse],
            summary="Получить приглашение по токену",
            description="Возвращает данные приглашения по токену ссылки-приглашения.",
            responses={
                200: {"description": "Данные приглашения"},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/{invitation_id}/accept",
            self.accept_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Принять приглашение",
            description="Принимает приглашение в workspace. Пользователь становится участником.",
            responses={
                200: {"description": "Приглашение принято"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
                409: {"description": "Участник уже существует или приглашение истекло", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/{invitation_id}/decline",
            self.decline_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отклонить приглашение",
            description="Отклоняет приглашение в workspace.",
            responses={
                200: {"description": "Приглашение отклонено"},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/mine",
            self.get_my_invitations,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceInvitationResponse],
            summary="Мои приглашения в workspace",
            description="Возвращает список приглашений текущего пользователя (PENDING по email, ACCEPTED/DECLINED по user_id).",
            responses={
                200: {"description": "Список приглашений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Workspace Invitations
    # ------------------------------------------------------------------

    async def get_invitations(
        self,
        ws_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceInvitationResponse]:
        """Список приглашений workspace."""
        handler = GetWorkspaceInvitationsHandler(
            invitation_repo=invitation_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceInvitationsQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [WorkspaceInvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def send_invitation(
        self,
        ws_id: str,
        body: SendWorkspaceInvitationRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> SuccessResponse[WorkspaceInvitationResponse]:
        """Отправить email-приглашение."""
        handler = SendWorkspaceInvitationHandler(
            invitation_repo=invitation_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SendWorkspaceInvitationCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            email=body.email,
            role_id=body.role_id,
            invited_by=caller_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WorkspaceInvitationResponse.model_validate(dto.model_dump()))

    async def send_bulk_invitations(
        self,
        ws_id: str,
        body: SendBulkWorkspaceInvitationsRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> PaginatedResponse[WorkspaceInvitationResponse]:
        """Массовая отправка приглашений."""
        handler = SendBulkWorkspaceInvitationsHandler(
            invitation_repo=invitation_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SendBulkWorkspaceInvitationsCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            emails=body.emails,
            role_id=body.role_id,
            invited_by=caller_id,
        )
        dto = await handler.handle(command)
        items = [WorkspaceInvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        return PaginatedResponse(items=items, total=dto.total, page=1, page_size=len(items))

    async def generate_invitation_link(
        self,
        ws_id: str,
        body: GenerateWorkspaceInvitationLinkRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> SuccessResponse[WorkspaceInvitationResponse]:
        """Сгенерировать ссылку-приглашение."""
        handler = GenerateWorkspaceInvitationLinkHandler(
            invitation_repo=invitation_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = GenerateWorkspaceInvitationLinkCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            role_id=body.role_id,
            invited_by=caller_id,
            expires_at=body.expires_at.isoformat() if body.expires_at else None,
            max_uses=body.max_uses,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WorkspaceInvitationResponse.model_validate(dto.model_dump()))

    async def revoke_invitation(
        self,
        ws_id: str,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Отозвать приглашение."""
        handler = RevokeWorkspaceInvitationHandler(
            invitation_repo=invitation_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RevokeWorkspaceInvitationCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            invitation_id=invitation_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Приглашение отозвано"})

    # ------------------------------------------------------------------
    # Invitation actions (not scoped under ws_id)
    # ------------------------------------------------------------------

    async def get_invitation_by_token(
        self,
        token: str,
        invitation_repo=Depends(get_workspace_invitation_repository),
    ) -> SuccessResponse[WorkspaceInvitationResponse]:
        """Получить приглашение по токену ссылки."""
        handler = GetWorkspaceInvitationByTokenHandler(invitation_repo=invitation_repo)
        query = GetWorkspaceInvitationByTokenQuery(token=token)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceInvitationResponse.model_validate(dto.model_dump()))

    async def accept_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        membership_repo=Depends(get_workspace_membership_repository),
        identity_port=Depends(get_ws_identity_user_port),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Принять приглашение."""
        handler = AcceptWorkspaceInvitationHandler(
            invitation_repo=invitation_repo,
            membership_repo=membership_repo,
            identity_port=identity_port,
            event_bus=event_bus,
        )
        command = AcceptWorkspaceInvitationCommand(
            invitation_id=invitation_id,
            user_id=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Приглашение принято"})

    async def decline_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        identity_port=Depends(get_ws_identity_user_port),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Отклонить приглашение."""
        handler = DeclineWorkspaceInvitationHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeclineWorkspaceInvitationCommand(
            invitation_id=invitation_id,
            user_id=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Приглашение отклонено"})

    # ------------------------------------------------------------------
    # My invitations
    # ------------------------------------------------------------------

    async def get_my_invitations(
        self,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        status: str | None = Query(default=None, description="Фильтр по статусу"),
        workspace_id: str | None = Query(default=None, description="Фильтр по workspace ID"),
        search_text: str | None = Query(default=None, description="Поиск по email"),
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_workspace_invitation_repository),
        identity_port=Depends(get_ws_identity_user_port),
    ) -> PaginatedResponse[WorkspaceInvitationResponse]:
        """Получить мои приглашения в workspace."""
        filters: dict = {}
        if status:
            filters["status"] = status
        if workspace_id:
            filters["workspace_id"] = workspace_id
        if search_text:
            filters["search_text"] = search_text

        handler = SearchMyWorkspaceInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
        )
        query = SearchMyWorkspaceInvitationsQuery(
            caller_id=caller_id,
            offset=offset,
            limit=limit,
            filters=filters or None,
        )
        dto = await handler.handle(query)
        items = [WorkspaceInvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)
