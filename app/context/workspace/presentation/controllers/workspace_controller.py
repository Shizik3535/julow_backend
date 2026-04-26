from __future__ import annotations

from typing import Any

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.commands.create_workspace import (
    CreateWorkspaceCommand,
    CreateWorkspaceHandler,
)
from app.context.workspace.application.commands.update_workspace_info import (
    UpdateWorkspaceInfoCommand,
    UpdateWorkspaceInfoHandler,
)
from app.context.workspace.application.commands.update_workspace_security_policy import (
    UpdateWorkspaceSecurityPolicyCommand,
    UpdateWorkspaceSecurityPolicyHandler,
)
from app.context.workspace.application.commands.update_workspace_membership_policy import (
    UpdateWorkspaceMembershipPolicyCommand,
    UpdateWorkspaceMembershipPolicyHandler,
)
from app.context.workspace.application.commands.update_workspace_limits import (
    UpdateWorkspaceLimitsCommand,
    UpdateWorkspaceLimitsHandler,
)
from app.context.workspace.application.commands.archive_workspace import (
    ArchiveWorkspaceCommand,
    ArchiveWorkspaceHandler,
)
from app.context.workspace.application.commands.restore_workspace import (
    RestoreWorkspaceCommand,
    RestoreWorkspaceHandler,
)
from app.context.workspace.application.commands.suspend_workspace import (
    SuspendWorkspaceCommand,
    SuspendWorkspaceHandler,
)
from app.context.workspace.application.commands.reactivate_workspace import (
    ReactivateWorkspaceCommand,
    ReactivateWorkspaceHandler,
)
from app.context.workspace.application.commands.request_workspace_deletion import (
    RequestWorkspaceDeletionCommand,
    RequestWorkspaceDeletionHandler,
)
from app.context.workspace.application.commands.transfer_workspace_ownership import (
    TransferWorkspaceOwnershipCommand,
    TransferWorkspaceOwnershipHandler,
)
from app.context.workspace.application.commands.move_workspace_under_parent import (
    MoveWorkspaceUnderParentCommand,
    MoveWorkspaceUnderParentHandler,
)
from app.context.workspace.application.commands.add_workspace_owner import (
    AddWorkspaceOwnerCommand,
    AddWorkspaceOwnerHandler,
)
from app.context.workspace.application.commands.remove_workspace_owner import (
    RemoveWorkspaceOwnerCommand,
    RemoveWorkspaceOwnerHandler,
)
from app.context.workspace.application.queries.search_workspaces import (
    SearchWorkspacesHandler,
    SearchWorkspacesQuery,
)
from app.context.workspace.application.queries.get_workspace import (
    GetWorkspaceHandler,
    GetWorkspaceQuery,
)
from app.context.workspace.application.queries.get_workspace_settings import (
    GetWorkspaceSettingsHandler,
    GetWorkspaceSettingsQuery,
)
from app.context.workspace.application.queries.get_child_workspaces import (
    GetChildWorkspacesHandler,
    GetChildWorkspacesQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_event_bus,
    get_workspace_membership_repository,
    get_workspace_permission_checker,
    get_workspace_repository,
    get_ws_identity_user_port,
    get_ws_org_permission_checker_port,
    get_workspace_role_repository,
)
from app.context.workspace.presentation.schemas.requests.create_workspace_request import CreateWorkspaceRequest
from app.context.workspace.presentation.schemas.requests.move_workspace_request import MoveWorkspaceRequest
from app.context.workspace.presentation.schemas.requests.suspend_workspace_request import SuspendWorkspaceRequest
from app.context.workspace.presentation.schemas.requests.transfer_workspace_ownership_request import (
    TransferWorkspaceOwnershipRequest,
)
from app.context.workspace.presentation.schemas.requests.update_workspace_info_request import UpdateWorkspaceInfoRequest
from app.context.workspace.presentation.schemas.requests.update_workspace_limits_request import (
    UpdateWorkspaceLimitsRequest,
)
from app.context.workspace.presentation.schemas.requests.update_workspace_membership_policy_request import (
    UpdateWorkspaceMembershipPolicyRequest,
)
from app.context.workspace.presentation.schemas.requests.update_workspace_security_policy_request import (
    UpdateWorkspaceSecurityPolicyRequest,
)
from app.context.workspace.presentation.schemas.requests.add_workspace_owner_request import AddWorkspaceOwnerRequest
from app.context.workspace.presentation.schemas.responses.workspace_response import WorkspaceResponse
from app.context.workspace.presentation.schemas.responses.workspace_settings_response import WorkspaceSettingsResponse


class WorkspaceController(BaseController):
    """
    Контроллер workspace.

    Endpoint'ы:
        POST   /                                        — Создать workspace
        GET    /                                        — Поиск workspace
        GET    /{ws_id}                                 — Получить workspace
        PATCH  /{ws_id}                                 — Обновить информацию
        PATCH  /{ws_id}/security-policy                 — Обновить политику безопасности
        PATCH  /{ws_id}/membership-policy               — Обновить политику членства
        PATCH  /{ws_id}/limits                          — Обновить лимиты
        POST   /{ws_id}/archive                         — Архивировать
        POST   /{ws_id}/restore                         — Восстановить из архива
        POST   /{ws_id}/suspend                         — Приостановить
        POST   /{ws_id}/reactivate                      — Реактивировать
        POST   /{ws_id}/request-deletion                 — Запросить удаление
        POST   /{ws_id}/transfer-ownership              — Передать владение
        POST   /{ws_id}/move                            — Переместить в иерархии
        GET    /{ws_id}/settings                        — Получить настройки
        GET    /{ws_id}/children                        — Дочерние workspace
        POST   /{ws_id}/owners                          — Добавить со-владельца
        DELETE /{ws_id}/owners/{user_id}                — Удалить со-владельца
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces", tags=["Workspace"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/",
            self.create_workspace,
            methods=["POST"],
            response_model=SuccessResponse[WorkspaceResponse],
            status_code=201,
            summary="Создать workspace",
            description="Создаёт новый workspace. Текущий пользователь становится владельцем.",
            responses={
                201: {"description": "Workspace создан"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав для создания в организации", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/",
            self.search_workspaces,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceResponse],
            summary="Поиск workspace",
            description="Пагинированный поиск workspace с фильтрацией.",
            responses={
                200: {"description": "Список workspace"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}",
            self.get_workspace,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceResponse],
            summary="Получить workspace",
            description="Возвращает данные workspace по UUID.",
            responses={
                200: {"description": "Данные workspace"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}",
            self.update_workspace_info,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить информацию workspace",
            description="Обновляет название, персонализацию и брендинг workspace.",
            responses={
                200: {"description": "Информация обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/security-policy",
            self.update_security_policy,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить политику безопасности",
            description="Обновляет политику безопасности workspace: PIN, пароль, IP-whitelist, SSO, 2FA и т.д.",
            responses={
                200: {"description": "Политика безопасности обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/membership-policy",
            self.update_membership_policy,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить политику членства",
            description="Обновляет политику членства: приглашения, роли, лимиты участников.",
            responses={
                200: {"description": "Политика членства обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/limits",
            self.update_limits,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить лимиты workspace",
            description="Обновляет лимиты: проекты, участники, хранилище, файлы, команды.",
            responses={
                200: {"description": "Лимиты обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/archive",
            self.archive_workspace,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Архивировать workspace",
            description="Архивирует workspace. Все проекты переходят в read-only.",
            responses={
                200: {"description": "Workspace архивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/restore",
            self.restore_workspace,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Восстановить workspace",
            description="Восстанавливает архивированный workspace.",
            responses={
                200: {"description": "Workspace восстановлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/suspend",
            self.suspend_workspace,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Приостановить workspace",
            description="Приостанавливает workspace с указанием причины.",
            responses={
                200: {"description": "Workspace приостановлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/reactivate",
            self.reactivate_workspace,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивировать workspace",
            description="Реактивирует приостановленный или архивированный workspace.",
            responses={
                200: {"description": "Workspace реактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/request-deletion",
            self.request_workspace_deletion,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Запросить удаление workspace",
            description="Инициирует процесс удаления workspace. Статус меняется на pending_deletion.",
            responses={
                200: {"description": "Запрос удаления принят"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/transfer-ownership",
            self.transfer_ownership,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Передать владение workspace",
            description="Передаёт владение workspace другому пользователю.",
            responses={
                200: {"description": "Владение передано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/move",
            self.move_workspace,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Переместить workspace в иерархии",
            description="Перемещает workspace под нового родителя или отсоединяет от текущего.",
            responses={
                200: {"description": "Workspace перемещён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Циклическая зависимость или нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/settings",
            self.get_workspace_settings,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceSettingsResponse],
            summary="Получить настройки workspace",
            description="Возвращает политики безопасности, членства и лимиты workspace.",
            responses={
                200: {"description": "Настройки workspace"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/children",
            self.get_child_workspaces,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceResponse],
            summary="Дочерние workspace",
            description="Возвращает список дочерних workspace.",
            responses={
                200: {"description": "Список дочерних workspace"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/owners",
            self.add_owner,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить со-владельца",
            description="Добавляет со-владельца workspace.",
            responses={
                200: {"description": "Со-владелец добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/owners/{user_id}",
            self.remove_owner,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить со-владельца",
            description="Удаляет со-владельца workspace.",
            responses={
                200: {"description": "Со-владелец удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Нельзя удалить последнего владельца", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Workspace CRUD
    # ------------------------------------------------------------------

    async def create_workspace(
        self,
        body: CreateWorkspaceRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        membership_repo=Depends(get_workspace_membership_repository),
        role_repo=Depends(get_workspace_role_repository),
        identity_port=Depends(get_ws_identity_user_port),
        org_permission_checker=Depends(get_ws_org_permission_checker_port),
        event_bus=Depends(get_workspace_event_bus),
    ) -> SuccessResponse[WorkspaceResponse]:
        """Создать workspace."""
        handler = CreateWorkspaceHandler(
            ws_repo=ws_repo,
            membership_repo=membership_repo,
            role_repo=role_repo,
            identity_port=identity_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = CreateWorkspaceCommand(
            caller_id=caller_id,
            owner_id=caller_id,
            name=body.name,
            workspace_type=body.workspace_type,
            organization_id=body.organization_id,
            parent_workspace_id=body.parent_workspace_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WorkspaceResponse.model_validate(dto.model_dump()))

    async def search_workspaces(
        self,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        organization_id: str | None = Query(default=None, description="Фильтр по ID организации"),
        status: str | None = Query(default=None, description="Фильтр по статусу"),
        workspace_type: str | None = Query(default=None, description="Фильтр по типу"),
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceResponse]:
        """Поиск workspace с пагинацией."""
        filters: dict[str, Any] = {}
        if organization_id:
            filters["organization_id"] = organization_id
        if status:
            filters["status"] = status
        if workspace_type:
            filters["workspace_type"] = workspace_type
        handler = SearchWorkspacesHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = SearchWorkspacesQuery(
            caller_id=caller_id,
            offset=offset,
            limit=limit,
            filters=filters or None,
        )
        dto = await handler.handle(query)
        items = [WorkspaceResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_workspace(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> SuccessResponse[WorkspaceResponse]:
        """Получить workspace по ID."""
        handler = GetWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceResponse.model_validate(dto.model_dump()))

    async def update_workspace_info(
        self,
        ws_id: str,
        body: UpdateWorkspaceInfoRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить информацию workspace."""
        handler = UpdateWorkspaceInfoHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceInfoCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            name=body.name,
            color=body.color,
            icon_url=body.icon_url,
            display_name=body.display_name,
            description=body.description,
            logo_url=body.logo_url,
            cover_image_url=body.cover_image_url,
            custom_css=body.custom_css,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Информация workspace обновлена"})

    async def update_security_policy(
        self,
        ws_id: str,
        body: UpdateWorkspaceSecurityPolicyRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить политику безопасности."""
        handler = UpdateWorkspaceSecurityPolicyHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceSecurityPolicyCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            pin_code_enabled=body.pin_code_enabled,
            password_enabled=body.password_enabled,
            ip_allowlist=body.ip_allowlist,
            sso_mode=body.sso_mode,
            require_2fa=body.require_2fa,
            session_timeout_minutes=body.session_timeout_minutes,
            inherit_from_parent=body.inherit_from_parent,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Политика безопасности обновлена"})

    async def update_membership_policy(
        self,
        ws_id: str,
        body: UpdateWorkspaceMembershipPolicyRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить политику членства."""
        handler = UpdateWorkspaceMembershipPolicyHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceMembershipPolicyCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            allow_invitation_links=body.allow_invitation_links,
            default_role=body.default_role,
            require_approval=body.require_approval,
            max_members=body.max_members,
            allowed_email_domains=body.allowed_email_domains,
            auto_add_from_org=body.auto_add_from_org,
            inherit_from_parent=body.inherit_from_parent,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Политика членства обновлена"})

    async def update_limits(
        self,
        ws_id: str,
        body: UpdateWorkspaceLimitsRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить лимиты workspace."""
        handler = UpdateWorkspaceLimitsHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceLimitsCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            max_projects=body.max_projects,
            max_members=body.max_members,
            max_storage_bytes=body.max_storage_bytes,
            max_file_size_bytes=body.max_file_size_bytes,
            max_teams=body.max_teams,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Лимиты workspace обновлены"})

    # ------------------------------------------------------------------
    # Workspace Lifecycle
    # ------------------------------------------------------------------

    async def archive_workspace(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Архивировать workspace."""
        handler = ArchiveWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ArchiveWorkspaceCommand(caller_id=caller_id, workspace_id=ws_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Workspace архивирован"})

    async def restore_workspace(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Восстановить workspace из архива."""
        handler = RestoreWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RestoreWorkspaceCommand(caller_id=caller_id, workspace_id=ws_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Workspace восстановлен"})

    async def suspend_workspace(
        self,
        ws_id: str,
        body: SuspendWorkspaceRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Приостановить workspace."""
        handler = SuspendWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SuspendWorkspaceCommand(caller_id=caller_id, workspace_id=ws_id, reason=body.reason)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Workspace приостановлен"})

    async def reactivate_workspace(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Реактивировать workspace."""
        handler = ReactivateWorkspaceHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateWorkspaceCommand(caller_id=caller_id, workspace_id=ws_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Workspace реактивирован"})

    async def request_workspace_deletion(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Запросить удаление workspace."""
        handler = RequestWorkspaceDeletionHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RequestWorkspaceDeletionCommand(caller_id=caller_id, workspace_id=ws_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Запрос удаления принят"})

    async def transfer_ownership(
        self,
        ws_id: str,
        body: TransferWorkspaceOwnershipRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Передать владение workspace."""
        handler = TransferWorkspaceOwnershipHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = TransferWorkspaceOwnershipCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            from_id=body.from_id,
            to_id=body.to_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Владение передано"})

    async def move_workspace(
        self,
        ws_id: str,
        body: MoveWorkspaceRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Переместить workspace в иерархии."""
        handler = MoveWorkspaceUnderParentHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = MoveWorkspaceUnderParentCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            parent_workspace_id=body.parent_workspace_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Workspace перемещён"})

    # ------------------------------------------------------------------
    # Workspace Settings & Hierarchy
    # ------------------------------------------------------------------

    async def get_workspace_settings(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> SuccessResponse[WorkspaceSettingsResponse]:
        """Получить настройки workspace."""
        handler = GetWorkspaceSettingsHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceSettingsQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceSettingsResponse.model_validate(dto.model_dump()))

    async def get_child_workspaces(
        self,
        ws_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceResponse]:
        """Получить дочерние workspace."""
        handler = GetChildWorkspacesHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetChildWorkspacesQuery(caller_id=caller_id, parent_workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [WorkspaceResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    # ------------------------------------------------------------------
    # Workspace Owners
    # ------------------------------------------------------------------

    async def add_owner(
        self,
        ws_id: str,
        body: AddWorkspaceOwnerRequest,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Добавить со-владельца workspace."""
        handler = AddWorkspaceOwnerHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddWorkspaceOwnerCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=body.user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Со-владелец добавлен"})

    async def remove_owner(
        self,
        ws_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Удалить со-владельца workspace."""
        handler = RemoveWorkspaceOwnerHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveWorkspaceOwnerCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Со-владелец удалён"})
