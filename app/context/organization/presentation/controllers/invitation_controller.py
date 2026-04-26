from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.send_invitation import (
    SendInvitationCommand,
    SendInvitationHandler,
)
from app.context.organization.application.commands.send_bulk_invitations import (
    SendBulkInvitationsCommand,
    SendBulkInvitationsHandler,
)
from app.context.organization.application.commands.generate_invitation_link import (
    GenerateInvitationLinkCommand,
    GenerateInvitationLinkHandler,
)
from app.context.organization.application.commands.revoke_invitation import (
    RevokeInvitationCommand,
    RevokeInvitationHandler,
)
from app.context.organization.application.commands.accept_invitation import (
    AcceptInvitationCommand,
    AcceptInvitationHandler,
)
from app.context.organization.application.commands.decline_invitation import (
    DeclineInvitationCommand,
    DeclineInvitationHandler,
)
from app.context.organization.application.queries.get_invitations_by_org import (
    GetInvitationsByOrgHandler,
    GetInvitationsByOrgQuery,
)
from app.context.organization.application.queries.get_invitation_by_token import (
    GetInvitationByTokenHandler,
    GetInvitationByTokenQuery,
)
from app.context.organization.application.queries.search_my_invitations import (
    SearchMyInvitationsHandler,
    SearchMyInvitationsQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_invitation_repository,
    get_org_identity_user_port,
    get_org_membership_repository,
    get_org_permission_checker,
    get_organization_event_bus,
    get_organization_repository,
)
from app.context.organization.presentation.schemas.requests.generate_invitation_link_request import (
    GenerateInvitationLinkRequest,
)
from app.context.organization.presentation.schemas.requests.send_bulk_invitations_request import (
    SendBulkInvitationsRequest,
)
from app.context.organization.presentation.schemas.requests.send_invitation_request import (
    SendInvitationRequest,
)
from app.context.organization.presentation.schemas.responses.invitation_response import (
    InvitationResponse,
)


class InvitationController(BaseController):
    """
    Контроллер приглашений организации.

    Endpoint'ы:
        GET    /{org_id}/invitations                           — Список приглашений
        POST   /{org_id}/invitations/email                     — Отправить email-приглашение
        POST   /{org_id}/invitations/bulk                      — Массовая отправка приглашений
        POST   /{org_id}/invitations/link                      — Сгенерировать ссылку-приглашение
        POST   /{org_id}/invitations/{invitation_id}/revoke    — Отозвать приглашение
        GET    /invitations/token/{token}                       — Получить приглашение по токену
        POST   /invitations/{invitation_id}/accept              — Принять приглашение
        POST   /invitations/{invitation_id}/decline             — Отклонить приглашение
        GET    /invitations/mine                                — Мои приглашения
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Invitations"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/invitations",
            self.get_invitations,
            methods=["GET"],
            response_model=SuccessResponse[list[InvitationResponse]],
            summary="Список приглашений организации",
            description="Возвращает список всех приглашений организации.",
            responses={
                200: {"description": "Список приглашений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/invitations/email",
            self.send_invitation,
            methods=["POST"],
            response_model=SuccessResponse[InvitationResponse],
            status_code=201,
            summary="Отправить email-приглашение",
            description="Отправляет приглашение на указанный email.",
            responses={
                201: {"description": "Приглашение отправлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Приглашение уже отправлено", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/invitations/bulk",
            self.send_bulk_invitations,
            methods=["POST"],
            response_model=SuccessResponse[list[InvitationResponse]],
            status_code=201,
            summary="Массовая отправка приглашений",
            description="Отправляет приглашения на список email-адресов. Дубликаты пропускаются.",
            responses={
                201: {"description": "Приглашения отправлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/invitations/link",
            self.generate_invitation_link,
            methods=["POST"],
            response_model=SuccessResponse[InvitationResponse],
            status_code=201,
            summary="Сгенерировать ссылку-приглашение",
            description="Генерирует ссылку-приглашение с опциональными ограничениями по использованию и времени.",
            responses={
                201: {"description": "Ссылка сгенерирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/invitations/{invitation_id}/revoke",
            self.revoke_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отозвать приглашение",
            description="Отзывает ранее отправленное приглашение.",
            responses={
                200: {"description": "Приглашение отозвано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/token/{token}",
            self.get_invitation_by_token,
            methods=["GET"],
            response_model=SuccessResponse[InvitationResponse],
            summary="Получить приглашение по токену",
            description="Возвращает данные приглашения по токену ссылки-приглашения.",
            responses={
                200: {"description": "Данные приглашения"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/{invitation_id}/accept",
            self.accept_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Принять приглашение",
            description="Принимает приглашение и добавляет пользователя в организацию.",
            responses={
                200: {"description": "Приглашение принято"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/{invitation_id}/decline",
            self.decline_invitation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отклонить приглашение",
            description="Отклоняет приглашение.",
            responses={
                200: {"description": "Приглашение отклонено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Приглашение не найдено", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/invitations/mine",
            self.get_my_invitations,
            methods=["GET"],
            response_model=SuccessResponse[list[InvitationResponse]],
            summary="Мои приглашения в организации",
            description="Возвращает список приглашений текущего пользователя (PENDING по email, ACCEPTED/DECLINED по user_id).",
            responses={
                200: {"description": "Список приглашений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Org-scoped invitations
    # ------------------------------------------------------------------

    async def get_invitations(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[list[InvitationResponse]]:
        """Получить список приглашений организации."""
        handler = GetInvitationsByOrgHandler(invitation_repo=invitation_repo, org_repo=org_repo, org_permission_checker=org_permission_checker)
        query = GetInvitationsByOrgQuery(caller_id=caller_id, org_id=org_id)
        dto = await handler.handle(query)
        items = [InvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def send_invitation(
        self,
        org_id: str,
        body: SendInvitationRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        invitation_repo=Depends(get_invitation_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[InvitationResponse]:
        """Отправить email-приглашение."""
        handler = SendInvitationHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = SendInvitationCommand(
            caller_id=caller_id,
            org_id=org_id,
            email=body.email,
            role_id=body.role_id,
            invited_by=caller_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=InvitationResponse.model_validate(dto.model_dump()))

    async def send_bulk_invitations(
        self,
        org_id: str,
        body: SendBulkInvitationsRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        invitation_repo=Depends(get_invitation_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[list[InvitationResponse]]:
        """Массовая отправка приглашений."""
        handler = SendBulkInvitationsHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = SendBulkInvitationsCommand(
            caller_id=caller_id,
            org_id=org_id,
            emails=body.emails,
            role_id=body.role_id,
            invited_by=caller_id,
        )
        dto = await handler.handle(command)
        items = [InvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def generate_invitation_link(
        self,
        org_id: str,
        body: GenerateInvitationLinkRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        invitation_repo=Depends(get_invitation_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[InvitationResponse]:
        """Сгенерировать ссылку-приглашение."""
        from datetime import datetime, timedelta, timezone

        expires_at: datetime | None = None
        if body.expires_in_hours is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=body.expires_in_hours)

        handler = GenerateInvitationLinkHandler(
            org_repo=org_repo,
            invitation_repo=invitation_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = GenerateInvitationLinkCommand(
            caller_id=caller_id,
            org_id=org_id,
            role_id=body.role_id,
            invited_by=caller_id,
            expires_at=expires_at,
            max_uses=body.max_uses,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=InvitationResponse.model_validate(dto.model_dump()))

    async def revoke_invitation(
        self,
        org_id: str,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Отозвать приглашение."""
        handler = RevokeInvitationHandler(
            invitation_repo=invitation_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RevokeInvitationCommand(
            caller_id=caller_id,
            org_id=org_id,
            invitation_id=invitation_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Приглашение отозвано")

    # ------------------------------------------------------------------
    # Global invitation actions
    # ------------------------------------------------------------------

    async def get_invitation_by_token(
        self,
        token: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
    ) -> SuccessResponse[InvitationResponse]:
        """Получить приглашение по токену."""
        handler = GetInvitationByTokenHandler(invitation_repo=invitation_repo)
        query = GetInvitationByTokenQuery(token=token)
        dto = await handler.handle(query)
        return SuccessResponse(data=InvitationResponse.model_validate(dto.model_dump()))

    async def accept_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
        membership_repo=Depends(get_org_membership_repository),
        identity_port=Depends(get_org_identity_user_port),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Принять приглашение."""
        handler = AcceptInvitationHandler(
            invitation_repo=invitation_repo,
            membership_repo=membership_repo,
            identity_port=identity_port,
            event_bus=event_bus,
        )
        command = AcceptInvitationCommand(
            invitation_id=invitation_id,
            user_id=caller_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Приглашение принято")

    async def decline_invitation(
        self,
        invitation_id: str,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
        identity_port=Depends(get_org_identity_user_port),
        permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Отклонить приглашение."""
        handler = DeclineInvitationHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeclineInvitationCommand(
            invitation_id=invitation_id,
            user_id=caller_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Приглашение отклонено")

    # ------------------------------------------------------------------
    # My invitations
    # ------------------------------------------------------------------

    async def get_my_invitations(
        self,
        offset: int = 0,
        limit: int = 100,
        status: str | None = None,
        org_id: str | None = None,
        search_text: str | None = None,
        caller_id: str = Depends(get_current_user_id),
        invitation_repo=Depends(get_invitation_repository),
        identity_port=Depends(get_org_identity_user_port),
    ) -> SuccessResponse[list[InvitationResponse]]:
        """Получить мои приглашения в организации."""
        filters: dict = {}
        if status:
            filters["status"] = status
        if org_id:
            filters["org_id"] = org_id
        if search_text:
            filters["search_text"] = search_text

        handler = SearchMyInvitationsHandler(
            invitation_repo=invitation_repo,
            identity_port=identity_port,
        )
        query = SearchMyInvitationsQuery(
            caller_id=caller_id,
            offset=offset,
            limit=limit,
            filters=filters or None,
        )
        dto = await handler.handle(query)
        items = [InvitationResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)
