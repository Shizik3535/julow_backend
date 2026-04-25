from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.add_sso_integration import (
    AddSSOIntegrationCommand,
    AddSSOIntegrationHandler,
)
from app.context.organization.application.commands.update_sso_integration import (
    UpdateSSOIntegrationCommand,
    UpdateSSOIntegrationHandler,
)
from app.context.organization.application.commands.deactivate_sso_integration import (
    DeactivateSSOIntegrationCommand,
    DeactivateSSOIntegrationHandler,
)
from app.context.organization.application.commands.add_org_storage import (
    AddOrgStorageCommand,
    AddOrgStorageHandler,
)
from app.context.organization.application.commands.update_org_storage import (
    UpdateOrgStorageCommand,
    UpdateOrgStorageHandler,
)
from app.context.organization.application.queries.get_sso_integrations import (
    GetSSOIntegrationsHandler,
    GetSSOIntegrationsQuery,
)
from app.context.organization.application.queries.get_org_storage import (
    GetOrgStorageHandler,
    GetOrgStorageQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_encryption_port,
    get_org_permission_checker,
    get_organization_event_bus,
    get_sso_integration_repository,
    get_storage_integration_repository,
)
from app.context.organization.presentation.schemas.requests.add_sso_integration_request import (
    AddSSOIntegrationRequest,
)
from app.context.organization.presentation.schemas.requests.add_org_storage_request import (
    AddOrgStorageRequest,
)
from app.context.organization.presentation.schemas.requests.update_sso_integration_request import (
    UpdateSSOIntegrationRequest,
)
from app.context.organization.presentation.schemas.requests.update_org_storage_request import (
    UpdateOrgStorageRequest,
)
from app.context.organization.presentation.schemas.responses.sso_integration_response import (
    SSOIntegrationResponse,
)
from app.context.organization.presentation.schemas.responses.storage_integration_response import (
    StorageIntegrationResponse,
)


class IntegrationController(BaseController):
    """
    Контроллер интеграций организации (SSO и хранилище).

    Endpoint'ы:
        GET    /{org_id}/sso-integrations                                — Список SSO-интеграций
        POST   /{org_id}/sso-integrations                                — Добавить SSO-интеграцию
        PATCH  /{org_id}/sso-integrations/{integration_id}               — Обновить SSO
        POST   /{org_id}/sso-integrations/{integration_id}/deactivate    — Деактивировать SSO
        GET    /{org_id}/storage                                         — Получить хранилище
        POST   /{org_id}/storage                                         — Добавить хранилище
        PATCH  /{org_id}/storage/{storage_id}                            — Обновить хранилище
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Integrations"])

    def _register_routes(self) -> None:
        # --- SSO ---
        self._router.add_api_route(
            "/{org_id}/sso-integrations",
            self.get_sso_integrations,
            methods=["GET"],
            response_model=SuccessResponse[list[SSOIntegrationResponse]],
            summary="Список SSO-интеграций",
            description="Возвращает список SSO-интеграций организации.",
            responses={
                200: {"description": "Список SSO-интеграций"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/sso-integrations",
            self.add_sso_integration,
            methods=["POST"],
            response_model=SuccessResponse[SSOIntegrationResponse],
            status_code=201,
            summary="Добавить SSO-интеграцию",
            description="Добавляет SSO-интеграцию в организацию. Сертификат шифруется.",
            responses={
                201: {"description": "SSO-интеграция добавлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/sso-integrations/{integration_id}",
            self.update_sso_integration,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить SSO-интеграцию",
            description="Обновляет параметры SSO-интеграции.",
            responses={
                200: {"description": "SSO-интеграция обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "SSO-интеграция не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/sso-integrations/{integration_id}/deactivate",
            self.deactivate_sso_integration,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать SSO-интеграцию",
            description="Деактивирует SSO-интеграцию без удаления.",
            responses={
                200: {"description": "SSO-интеграция деактивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "SSO-интеграция не найдена", "model": ErrorResponse},
            },
        )

        # --- Storage ---
        self._router.add_api_route(
            "/{org_id}/storage",
            self.get_storage,
            methods=["GET"],
            response_model=SuccessResponse[StorageIntegrationResponse],
            summary="Получить хранилище организации",
            description="Возвращает данные хранилища организации.",
            responses={
                200: {"description": "Данные хранилища"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Хранилище не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/storage",
            self.add_storage,
            methods=["POST"],
            response_model=SuccessResponse[StorageIntegrationResponse],
            status_code=201,
            summary="Добавить хранилище",
            description="Добавляет хранилище в организацию. Ключ доступа шифруется.",
            responses={
                201: {"description": "Хранилище добавлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/storage/{storage_id}",
            self.update_storage,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить хранилище",
            description="Обновляет конфигурацию и/или квоту хранилища.",
            responses={
                200: {"description": "Хранилище обновлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Хранилище не найдено", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # SSO Integrations
    # ------------------------------------------------------------------

    async def get_sso_integrations(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        sso_repo=Depends(get_sso_integration_repository),
    ) -> SuccessResponse[list[SSOIntegrationResponse]]:
        """Получить список SSO-интеграций."""
        handler = GetSSOIntegrationsHandler(sso_repo=sso_repo)
        query = GetSSOIntegrationsQuery(org_id=org_id)
        dto = await handler.handle(query)
        items = [SSOIntegrationResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def add_sso_integration(
        self,
        org_id: str,
        body: AddSSOIntegrationRequest,
        caller_id: str = Depends(get_current_user_id),
        sso_repo=Depends(get_sso_integration_repository),
        encryption_port=Depends(get_encryption_port),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[SSOIntegrationResponse]:
        """Добавить SSO-интеграцию."""
        handler = AddSSOIntegrationHandler(
            sso_repo=sso_repo,
            encryption_port=encryption_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddSSOIntegrationCommand(
            caller_id=caller_id,
            org_id=org_id,
            provider=body.provider,
            entity_id=body.entity_id,
            sso_url=body.sso_url,
            certificate=body.certificate,
            added_by=caller_id,
            group_mapping=body.group_mapping,
            attribute_mapping=body.attribute_mapping,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=SSOIntegrationResponse.model_validate(dto.model_dump()))

    async def update_sso_integration(
        self,
        org_id: str,
        integration_id: str,
        body: UpdateSSOIntegrationRequest,
        caller_id: str = Depends(get_current_user_id),
        sso_repo=Depends(get_sso_integration_repository),
        encryption_port=Depends(get_encryption_port),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить SSO-интеграцию."""
        handler = UpdateSSOIntegrationHandler(
            sso_repo=sso_repo,
            encryption_port=encryption_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateSSOIntegrationCommand(
            caller_id=caller_id,
            org_id=org_id,
            integration_id=integration_id,
            entity_id=body.entity_id,
            sso_url=body.sso_url,
            certificate=body.certificate,
            group_mapping=body.group_mapping,
            attribute_mapping=body.attribute_mapping,
        )
        await handler.handle(command)
        return MessageResponse(message="SSO-интеграция обновлена")

    async def deactivate_sso_integration(
        self,
        org_id: str,
        integration_id: str,
        caller_id: str = Depends(get_current_user_id),
        sso_repo=Depends(get_sso_integration_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Деактивировать SSO-интеграцию."""
        handler = DeactivateSSOIntegrationHandler(
            sso_repo=sso_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateSSOIntegrationCommand(
            caller_id=caller_id,
            org_id=org_id,
            integration_id=integration_id,
        )
        await handler.handle(command)
        return MessageResponse(message="SSO-интеграция деактивирована")

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def get_storage(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_integration_repository),
    ) -> SuccessResponse[StorageIntegrationResponse]:
        """Получить хранилище организации."""
        handler = GetOrgStorageHandler(storage_repo=storage_repo)
        query = GetOrgStorageQuery(org_id=org_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=StorageIntegrationResponse.model_validate(dto.model_dump()))

    async def add_storage(
        self,
        org_id: str,
        body: AddOrgStorageRequest,
        caller_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_integration_repository),
        encryption_port=Depends(get_encryption_port),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[StorageIntegrationResponse]:
        """Добавить хранилище."""
        handler = AddOrgStorageHandler(
            storage_repo=storage_repo,
            encryption_port=encryption_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddOrgStorageCommand(
            caller_id=caller_id,
            org_id=org_id,
            provider=body.provider,
            endpoint=body.endpoint,
            bucket=body.bucket,
            region=body.region,
            access_key=body.access_key,
            max_bytes=body.max_bytes,
            max_file_size_bytes=body.max_file_size_bytes,
            allowed_extensions=body.allowed_extensions,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=StorageIntegrationResponse.model_validate(dto.model_dump()))

    async def update_storage(
        self,
        org_id: str,
        storage_id: str,
        body: UpdateOrgStorageRequest,
        caller_id: str = Depends(get_current_user_id),
        storage_repo=Depends(get_storage_integration_repository),
        encryption_port=Depends(get_encryption_port),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить хранилище."""
        handler = UpdateOrgStorageHandler(
            storage_repo=storage_repo,
            encryption_port=encryption_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateOrgStorageCommand(
            caller_id=caller_id,
            org_id=org_id,
            storage_id=storage_id,
            provider=body.provider,
            endpoint=body.endpoint,
            bucket=body.bucket,
            region=body.region,
            access_key=body.access_key,
            max_bytes=body.max_bytes,
            max_file_size_bytes=body.max_file_size_bytes,
            allowed_extensions=body.allowed_extensions,
        )
        await handler.handle(command)
        return MessageResponse(message="Хранилище обновлено")
