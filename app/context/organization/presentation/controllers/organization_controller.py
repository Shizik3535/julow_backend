from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.create_organization import (
    CreateOrganizationCommand,
    CreateOrganizationHandler,
)
from app.context.organization.application.commands.update_organization_info import (
    UpdateOrganizationInfoCommand,
    UpdateOrganizationInfoHandler,
)
from app.context.organization.application.commands.update_security_policy import (
    UpdateSecurityPolicyCommand,
    UpdateSecurityPolicyHandler,
)
from app.context.organization.application.commands.update_membership_policy import (
    UpdateMembershipPolicyCommand,
    UpdateMembershipPolicyHandler,
)
from app.context.organization.application.commands.suspend_organization import (
    SuspendOrganizationCommand,
    SuspendOrganizationHandler,
)
from app.context.organization.application.commands.reactivate_organization import (
    ReactivateOrganizationCommand,
    ReactivateOrganizationHandler,
)
from app.context.organization.application.commands.request_organization_deletion import (
    RequestOrganizationDeletionCommand,
    RequestOrganizationDeletionHandler,
)
from app.context.organization.application.commands.transfer_ownership import (
    TransferOwnershipCommand,
    TransferOwnershipHandler,
)
from app.context.organization.application.queries.get_organization import (
    GetOrganizationHandler,
    GetOrganizationQuery,
)
from app.context.organization.application.queries.search_organizations import (
    SearchOrganizationsHandler,
    SearchOrganizationsQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_org_identity_user_port,
    get_org_membership_repository,
    get_org_permission_checker,
    get_org_role_repository,
    get_organization_event_bus,
    get_organization_repository,
)
from app.context.organization.presentation.schemas.requests.create_organization_request import (
    CreateOrganizationRequest,
)
from app.context.organization.presentation.schemas.requests.suspend_organization_request import (
    SuspendOrganizationRequest,
)
from app.context.organization.presentation.schemas.requests.transfer_ownership_request import (
    TransferOwnershipRequest,
)
from app.context.organization.presentation.schemas.requests.update_membership_policy_request import (
    UpdateMembershipPolicyRequest,
)
from app.context.organization.presentation.schemas.requests.update_organization_info_request import (
    UpdateOrganizationInfoRequest,
)
from app.context.organization.presentation.schemas.requests.update_security_policy_request import (
    UpdateSecurityPolicyRequest,
)
from app.context.organization.presentation.schemas.responses.organization_response import (
    OrganizationResponse,
)


class OrganizationController(BaseController):
    """
    Контроллер организаций.

    Endpoint'ы:
        POST   /                              — Создать организацию
        GET    /                              — Поиск организаций
        GET    /{org_id}                      — Получить организацию
        PATCH  /{org_id}                      — Обновить информацию
        PATCH  /{org_id}/security-policy      — Обновить политику безопасности
        PATCH  /{org_id}/membership-policy    — Обновить политику членства
        POST   /{org_id}/suspend              — Приостановить организацию
        POST   /{org_id}/reactivate           — Реактивировать организацию
        POST   /{org_id}/request-deletion     — Запросить удаление
        POST   /{org_id}/transfer-ownership   — Передать владение
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/",
            self.create_organization,
            methods=["POST"],
            response_model=SuccessResponse[OrganizationResponse],
            status_code=201,
            summary="Создать организацию",
            description="Создаёт новую организацию. Текущий пользователь становится владельцем.",
            responses={
                201: {"description": "Организация создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/",
            self.search_organizations,
            methods=["GET"],
            response_model=PaginatedResponse[OrganizationResponse],
            summary="Поиск организаций",
            description="Пагинированный поиск организаций с фильтрацией.",
            responses={
                200: {"description": "Список организаций"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}",
            self.get_organization,
            methods=["GET"],
            response_model=SuccessResponse[OrganizationResponse],
            summary="Получить организацию",
            description="Возвращает данные организации по UUID.",
            responses={
                200: {"description": "Данные организации"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}",
            self.update_organization_info,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить информацию организации",
            description="Обновляет название, персонализацию и брендинг организации.",
            responses={
                200: {"description": "Информация обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/security-policy",
            self.update_security_policy,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить политику безопасности",
            description="Обновляет политику безопасности организации: 2FA, длина пароля, таймаут сессии и т.д.",
            responses={
                200: {"description": "Политика безопасности обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/membership-policy",
            self.update_membership_policy,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить политику членства",
            description="Обновляет политику членства: приглашения, роли, лимиты участников.",
            responses={
                200: {"description": "Политика членства обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/suspend",
            self.suspend_organization,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Приостановить организацию",
            description="Приостанавливает организацию с указанием причины.",
            responses={
                200: {"description": "Организация приостановлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/reactivate",
            self.reactivate_organization,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивировать организацию",
            description="Реактивирует приостановленную организацию.",
            responses={
                200: {"description": "Организация реактивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/request-deletion",
            self.request_organization_deletion,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Запросить удаление организации",
            description="Инициирует процесс удаления организации. Статус меняется на pending_deletion.",
            responses={
                200: {"description": "Запрос удаления принят"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/transfer-ownership",
            self.transfer_ownership,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Передать владение организацией",
            description="Передаёт владение организацией другому пользователю.",
            responses={
                200: {"description": "Владение передано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Organization CRUD
    # ------------------------------------------------------------------

    async def create_organization(
        self,
        body: CreateOrganizationRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        membership_repo=Depends(get_org_membership_repository),
        role_repo=Depends(get_org_role_repository),
        identity_port=Depends(get_org_identity_user_port),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[OrganizationResponse]:
        """Создать организацию."""
        handler = CreateOrganizationHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_role_repo=role_repo,
            identity_port=identity_port,
            event_bus=event_bus,
        )
        command = CreateOrganizationCommand(
            owner_id=caller_id,
            name=body.name,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=OrganizationResponse.model_validate(dto.model_dump()))

    async def search_organizations(
        self,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> PaginatedResponse[OrganizationResponse]:
        """Поиск организаций с пагинацией."""
        handler = SearchOrganizationsHandler(org_repo=org_repo, org_permission_checker=org_permission_checker)
        query = SearchOrganizationsQuery(caller_id=caller_id, offset=offset, limit=limit)
        dto = await handler.handle(query)
        items = [OrganizationResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_organization(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[OrganizationResponse]:
        """Получить организацию по ID."""
        handler = GetOrganizationHandler(org_repo=org_repo, org_permission_checker=org_permission_checker)
        query = GetOrganizationQuery(caller_id=caller_id, org_id=org_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=OrganizationResponse.model_validate(dto.model_dump()))

    async def update_organization_info(
        self,
        org_id: str,
        body: UpdateOrganizationInfoRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить информацию организации."""
        handler = UpdateOrganizationInfoHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateOrganizationInfoCommand(
            caller_id=caller_id,
            org_id=org_id,
            name=body.name,
            personalization_color=body.personalization_color,
            personalization_icon=body.personalization_icon,
            personalization_display_name=body.personalization_display_name,
            personalization_custom_domain=body.personalization_custom_domain,
            branding_logo_url=body.branding_logo_url,
            branding_favicon_url=body.branding_favicon_url,
            branding_custom_css=body.branding_custom_css,
            branding_login_message=body.branding_login_message,
        )
        await handler.handle(command)
        return MessageResponse(message="Информация организации обновлена")

    async def update_security_policy(
        self,
        org_id: str,
        body: UpdateSecurityPolicyRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить политику безопасности."""
        handler = UpdateSecurityPolicyHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateSecurityPolicyCommand(
            caller_id=caller_id,
            org_id=org_id,
            require_2fa=body.require_2fa,
            password_min_length=body.password_min_length,
            session_timeout_minutes=body.session_timeout_minutes,
            ip_allowlist=body.ip_allowlist,
            domain_restrictions=body.domain_restrictions,
            require_email_verification=body.require_email_verification,
        )
        await handler.handle(command)
        return MessageResponse(message="Политика безопасности обновлена")

    async def update_membership_policy(
        self,
        org_id: str,
        body: UpdateMembershipPolicyRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить политику членства."""
        handler = UpdateMembershipPolicyHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateMembershipPolicyCommand(
            caller_id=caller_id,
            org_id=org_id,
            allow_invitation_links=body.allow_invitation_links,
            default_role=body.default_role,
            require_approval=body.require_approval,
            max_members=body.max_members,
            allowed_email_domains=body.allowed_email_domains,
        )
        await handler.handle(command)
        return MessageResponse(message="Политика членства обновлена")

    async def suspend_organization(
        self,
        org_id: str,
        body: SuspendOrganizationRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Приостановить организацию."""
        handler = SuspendOrganizationHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = SuspendOrganizationCommand(
            caller_id=caller_id,
            org_id=org_id,
            reason=body.reason,
        )
        await handler.handle(command)
        return MessageResponse(message="Организация приостановлена")

    async def reactivate_organization(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Реактивировать организацию."""
        handler = ReactivateOrganizationHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateOrganizationCommand(
            caller_id=caller_id,
            org_id=org_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Организация реактивирована")

    async def request_organization_deletion(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Запросить удаление организации."""
        handler = RequestOrganizationDeletionHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RequestOrganizationDeletionCommand(
            caller_id=caller_id,
            org_id=org_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Запрос удаления организации принят")

    async def transfer_ownership(
        self,
        org_id: str,
        body: TransferOwnershipRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Передать владение организацией."""
        handler = TransferOwnershipHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = TransferOwnershipCommand(
            caller_id=caller_id,
            org_id=org_id,
            from_id=body.from_id,
            to_id=body.to_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Владение организацией передано")
