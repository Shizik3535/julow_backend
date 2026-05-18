from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.project.application.commands.send_project_invitation import (
    SendProjectInvitationCommand,
    SendProjectInvitationHandler,
)
from app.context.project.application.commands.generate_project_invitation_link import (
    GenerateProjectInvitationLinkCommand,
    GenerateProjectInvitationLinkHandler,
)
from app.context.project.application.commands.revoke_project_invitation import (
    RevokeProjectInvitationCommand,
    RevokeProjectInvitationHandler,
)
from app.context.project.application.commands.accept_project_invitation import (
    AcceptProjectInvitationCommand,
    AcceptProjectInvitationHandler,
)
from app.context.project.application.commands.decline_project_invitation import (
    DeclineProjectInvitationCommand,
    DeclineProjectInvitationHandler,
)
from app.context.project.application.queries.get_project_invitations import (
    GetProjectInvitationsHandler,
    GetProjectInvitationsQuery,
)
from app.context.project.application.queries.get_project_invitation_by_token import (
    GetProjectInvitationByTokenHandler,
    GetProjectInvitationByTokenQuery,
)
from app.context.project.application.queries.get_my_project_invitations import (
    GetMyProjectInvitationsHandler,
    GetMyProjectInvitationsQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_identity_user_port,
    get_project_invitation_repository,
    get_project_membership_repository,
    get_project_permission_checker,
    get_project_repository,
    get_project_workspace_membership_port,
)
from app.context.project.presentation.schemas.requests.generate_project_invitation_link_request import (
    GenerateProjectInvitationLinkRequest,
)
from app.context.project.presentation.schemas.requests.redeem_project_invitation_request import (
    RedeemProjectInvitationRequest,
)
from app.context.project.presentation.schemas.requests.send_project_invitation_request import (
    SendProjectInvitationRequest,
)
from app.context.project.presentation.schemas.responses.project_invitation_response import (
    ProjectInvitationResponse,
)


class ProjectInvitationController(BaseController):
    """
    Контроллер приглашений в проект.

    Endpoint'ы (project-scoped):
        GET    /workspaces/{ws_id}/projects/{project_id}/invitations          — список приглашений
        POST   /workspaces/{ws_id}/projects/{project_id}/invitations/email    — email-приглашение
        POST   /workspaces/{ws_id}/projects/{project_id}/invitations/link     — сгенерировать ссылку/код
        POST   /workspaces/{ws_id}/projects/{project_id}/invitations/{id}/revoke — отозвать

    Endpoint'ы (без project_id, для приглашённых):
        GET    /project-invitations/token/{token}      — получить инфо по коду/ссылке
        POST   /project-invitations/{id}/accept        — принять приглашение по id
        POST   /project-invitations/{id}/decline       — отклонить приглашение
        POST   /project-invitations/redeem             — принять по коду/токену (без id)
        GET    /project-invitations/mine               — мои приглашения
    """

    def __init__(self) -> None:
        super().__init__(prefix="", tags=["Project / Invitations"])

    def _register_routes(self) -> None:
        # ── Project-scoped (управление приглашениями владельцем) ──
        self._router.add_api_route(
            "/workspaces/{ws_id}/projects/{project_id}/invitations",
            self.list_invitations,
            methods=["GET"],
            response_model=PaginatedResponse[ProjectInvitationResponse],
            summary="Список приглашений проекта",
            responses={
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Проект не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/workspaces/{ws_id}/projects/{project_id}/invitations/email",
            self.send_email_invitation,
            methods=["POST"],
            response_model=SuccessResponse[ProjectInvitationResponse],
            status_code=201,
            summary="Отправить email-приглашение в проект",
        )
        self._router.add_api_route(
            "/workspaces/{ws_id}/projects/{project_id}/invitations/link",
            self.generate_invitation_link,
            methods=["POST"],
            response_model=SuccessResponse[ProjectInvitationResponse],
            status_code=201,
            summary="Сгенерировать ссылку/код-приглашение в проект",
        )
        self._router.add_api_route(
            "/workspaces/{ws_id}/projects/{project_id}/invitations/{invitation_id}/revoke",
            self.revoke_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отозвать приглашение",
        )

        # ── Receiver-side endpoints (без project_id в URL) ──
        self._router.add_api_route(
            "/project-invitations/token/{token}",
            self.get_invitation_by_token,
            methods=["GET"],
            response_model=SuccessResponse[ProjectInvitationResponse],
            summary="Получить приглашение по токену/коду",
            responses={404: {"description": "Приглашение не найдено", "model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/project-invitations/{invitation_id}/accept",
            self.accept_invitation,
            methods=["POST"],
            response_model=SuccessResponse[dict],
            summary="Принять приглашение по ID",
        )
        self._router.add_api_route(
            "/project-invitations/{invitation_id}/decline",
            self.decline_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отклонить приглашение",
        )
        self._router.add_api_route(
            "/project-invitations/redeem",
            self.redeem_invitation,
            methods=["POST"],
            response_model=SuccessResponse[dict],
            summary="Принять приглашение по коду/токену",
        )
        self._router.add_api_route(
            "/project-invitations/mine",
            self.get_my_invitations,
            methods=["GET"],
            response_model=PaginatedResponse[ProjectInvitationResponse],
            summary="Мои приглашения в проекты",
        )

    # ------------------------------------------------------------------
    # Project-scoped (управление владельцем)
    # ------------------------------------------------------------------

    async def list_invitations(
        self,
        ws_id: str,
        project_id: str,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> PaginatedResponse[ProjectInvitationResponse]:
        handler = GetProjectInvitationsHandler(
            invitation_repo=invitation_repo,
            project_repo=project_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetProjectInvitationsQuery(
            caller_id=caller_id, project_id=project_id,
        ))
        items = [ProjectInvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def send_email_invitation(
        self,
        ws_id: str,
        project_id: str,
        body: SendProjectInvitationRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[ProjectInvitationResponse]:
        handler = SendProjectInvitationHandler(
            invitation_repo=invitation_repo,
            project_repo=project_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(SendProjectInvitationCommand(
            caller_id=caller_id,
            project_id=project_id,
            email=body.email,
            role_id=body.role_id,
        ))
        return SuccessResponse(data=ProjectInvitationResponse.model_validate(dto.model_dump()))

    async def generate_invitation_link(
        self,
        ws_id: str,
        project_id: str,
        body: GenerateProjectInvitationLinkRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[ProjectInvitationResponse]:
        handler = GenerateProjectInvitationLinkHandler(
            invitation_repo=invitation_repo,
            project_repo=project_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(GenerateProjectInvitationLinkCommand(
            caller_id=caller_id,
            project_id=project_id,
            role_id=body.role_id,
            expires_at=body.expires_at.isoformat() if body.expires_at else None,
            max_uses=body.max_uses,
        ))
        return SuccessResponse(data=ProjectInvitationResponse.model_validate(dto.model_dump()))

    async def revoke_invitation(
        self,
        ws_id: str,
        project_id: str,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RevokeProjectInvitationHandler(
            invitation_repo=invitation_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        await handler.handle(RevokeProjectInvitationCommand(
            caller_id=caller_id, project_id=project_id, invitation_id=invitation_id,
        ))
        return SuccessResponse(data={"message": "Приглашение отозвано"})

    # ------------------------------------------------------------------
    # Receiver-side
    # ------------------------------------------------------------------

    async def get_invitation_by_token(
        self,
        token: str,
        invitation_repo=Depends(get_project_invitation_repository),
        project_repo=Depends(get_project_repository),
    ) -> SuccessResponse[ProjectInvitationResponse]:
        handler = GetProjectInvitationByTokenHandler(
            invitation_repo=invitation_repo,
            project_repo=project_repo,
        )
        dto = await handler.handle(GetProjectInvitationByTokenQuery(token=token))
        return SuccessResponse(data=ProjectInvitationResponse.model_validate(dto.model_dump()))

    async def accept_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        membership_repo=Depends(get_project_membership_repository),
        identity_port=Depends(get_project_identity_user_port),
        workspace_membership_port=Depends(get_project_workspace_membership_port),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[dict]:
        handler = AcceptProjectInvitationHandler(
            invitation_repo=invitation_repo,
            membership_repo=membership_repo,
            identity_port=identity_port,
            workspace_membership_port=workspace_membership_port,
            event_bus=event_bus,
        )
        result = await handler.handle(AcceptProjectInvitationCommand(
            invitation_id=invitation_id, user_id=caller_id,
        ))
        return SuccessResponse(data=result)

    async def decline_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        identity_port=Depends(get_project_identity_user_port),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = DeclineProjectInvitationHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
            event_bus=event_bus,
        )
        await handler.handle(DeclineProjectInvitationCommand(
            invitation_id=invitation_id, user_id=caller_id,
        ))
        return SuccessResponse(data={"message": "Приглашение отклонено"})

    async def redeem_invitation(
        self,
        body: RedeemProjectInvitationRequest,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        membership_repo=Depends(get_project_membership_repository),
        identity_port=Depends(get_project_identity_user_port),
        workspace_membership_port=Depends(get_project_workspace_membership_port),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[dict]:
        handler = AcceptProjectInvitationHandler(
            invitation_repo=invitation_repo,
            membership_repo=membership_repo,
            identity_port=identity_port,
            workspace_membership_port=workspace_membership_port,
            event_bus=event_bus,
        )
        result = await handler.handle(AcceptProjectInvitationCommand(
            token=body.token, user_id=caller_id,
        ))
        return SuccessResponse(data=result)

    async def get_my_invitations(
        self,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
        status: str | None = Query(default=None),
        project_id: str | None = Query(default=None),
        search_text: str | None = Query(default=None),
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_project_invitation_repository),
        identity_port=Depends(get_project_identity_user_port),
    ) -> PaginatedResponse[ProjectInvitationResponse]:
        filters: dict = {}
        if status:
            filters["status"] = status
        if project_id:
            filters["project_id"] = project_id
        if search_text:
            filters["search_text"] = search_text

        handler = GetMyProjectInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
        )
        dto = await handler.handle(GetMyProjectInvitationsQuery(
            caller_id=caller_id,
            offset=offset,
            limit=limit,
            filters=filters or None,
        ))
        items = [ProjectInvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)
