from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.project.application.commands.create_project import (
    CreateProjectCommand,
    CreateProjectHandler,
)
from app.context.project.application.commands.update_project_info import (
    UpdateProjectInfoCommand,
    UpdateProjectInfoHandler,
)
from app.context.project.application.commands.archive_project import (
    ArchiveProjectCommand,
    ArchiveProjectHandler,
)
from app.context.project.application.commands.restore_project import (
    RestoreProjectCommand,
    RestoreProjectHandler,
)
from app.context.project.application.commands.suspend_project import (
    SuspendProjectCommand,
    SuspendProjectHandler,
)
from app.context.project.application.commands.reactivate_project import (
    ReactivateProjectCommand,
    ReactivateProjectHandler,
)
from app.context.project.application.commands.request_project_deletion import (
    RequestProjectDeletionCommand,
    RequestProjectDeletionHandler,
)
from app.context.project.application.commands.transfer_project_ownership import (
    TransferProjectOwnershipCommand,
    TransferProjectOwnershipHandler,
)
from app.context.project.application.commands.change_project_methodology import (
    ChangeProjectMethodologyCommand,
    ChangeProjectMethodologyHandler,
)
from app.context.project.application.commands.change_project_visibility import (
    ChangeProjectVisibilityCommand,
    ChangeProjectVisibilityHandler,
)
from app.context.project.application.commands.add_project_owner import (
    AddProjectOwnerCommand,
    AddProjectOwnerHandler,
)
from app.context.project.application.commands.remove_project_owner import (
    RemoveProjectOwnerCommand,
    RemoveProjectOwnerHandler,
)
from app.context.project.application.commands.add_project_custom_field import (
    AddProjectCustomFieldCommand,
    AddProjectCustomFieldHandler,
)
from app.context.project.application.commands.update_project_custom_field import (
    UpdateProjectCustomFieldCommand,
    UpdateProjectCustomFieldHandler,
)
from app.context.project.application.commands.remove_project_custom_field import (
    RemoveProjectCustomFieldCommand,
    RemoveProjectCustomFieldHandler,
)
from app.context.project.application.commands.add_project_milestone import (
    AddProjectMilestoneCommand,
    AddProjectMilestoneHandler,
)
from app.context.project.application.commands.update_project_milestone import (
    UpdateProjectMilestoneCommand,
    UpdateProjectMilestoneHandler,
)
from app.context.project.application.commands.change_project_milestone_status import (
    ChangeProjectMilestoneStatusCommand,
    ChangeProjectMilestoneStatusHandler,
)
from app.context.project.application.queries.get_project import (
    GetProjectHandler,
    GetProjectQuery,
)
from app.context.project.application.queries.get_projects_by_workspace import (
    GetProjectsByWorkspaceHandler,
    GetProjectsByWorkspaceQuery,
)
from app.context.project.application.queries.get_archived_projects import (
    GetArchivedProjectsHandler,
    GetArchivedProjectsQuery,
)
from app.context.project.application.queries.get_overdue_projects import (
    GetOverdueProjectsHandler,
    GetOverdueProjectsQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_identity_user_port,
    get_project_membership_repository,
    get_project_permission_checker,
    get_project_repository,
    get_project_workspace_membership_port,
    get_project_workspace_port,
    get_project_ws_permission_checker_port,
    get_board_repository,
    get_project_role_repository,
    get_sprint_repository,
)
from app.context.project.presentation.schemas.requests.add_project_custom_field_request import (
    AddProjectCustomFieldRequest,
)
from app.context.project.presentation.schemas.requests.add_project_milestone_request import (
    AddProjectMilestoneRequest,
)
from app.context.project.presentation.schemas.requests.add_project_owner_request import (
    AddProjectOwnerRequest,
)
from app.context.project.presentation.schemas.requests.change_project_methodology_request import (
    ChangeProjectMethodologyRequest,
)
from app.context.project.presentation.schemas.requests.change_project_milestone_status_request import (
    ChangeProjectMilestoneStatusRequest,
)
from app.context.project.presentation.schemas.requests.change_project_visibility_request import (
    ChangeProjectVisibilityRequest,
)
from app.context.project.presentation.schemas.requests.create_project_request import (
    CreateProjectRequest,
)
from app.context.project.presentation.schemas.requests.suspend_project_request import (
    SuspendProjectRequest,
)
from app.context.project.presentation.schemas.requests.transfer_project_ownership_request import (
    TransferProjectOwnershipRequest,
)
from app.context.project.presentation.schemas.requests.update_project_custom_field_request import (
    UpdateProjectCustomFieldRequest,
)
from app.context.project.presentation.schemas.requests.update_project_info_request import (
    UpdateProjectInfoRequest,
)
from app.context.project.presentation.schemas.requests.update_project_milestone_request import (
    UpdateProjectMilestoneRequest,
)
from app.context.project.presentation.schemas.responses.milestone_response import (
    MilestoneResponse,
)
from app.context.project.presentation.schemas.responses.project_response import (
    ProjectResponse,
)


class ProjectController(BaseController):
    """
    Контроллер проектов workspace.

    Endpoint'ы:
        POST   /                                         — Создать проект
        GET    /                                         — Список проектов workspace
        GET    /archived                                 — Архивированные проекты
        GET    /overdue                                  — Просроченные проекты
        GET    /{project_id}                             — Получить проект
        PATCH  /{project_id}                             — Обновить информацию
        POST   /{project_id}/archive                     — Архивировать
        POST   /{project_id}/restore                     — Восстановить
        POST   /{project_id}/suspend                     — Приостановить
        POST   /{project_id}/reactivate                   — Реактивировать
        POST   /{project_id}/request-deletion             — Запросить удаление
        POST   /{project_id}/transfer-ownership           — Передать владение
        PATCH  /{project_id}/methodology                  — Сменить методологию
        PATCH  /{project_id}/visibility                   — Сменить видимость
        POST   /{project_id}/owners                       — Добавить со-владельца
        DELETE /{project_id}/owners/{user_id}             — Удалить со-владельца
        POST   /{project_id}/custom-fields                — Добавить кастомное поле
        PATCH  /{project_id}/custom-fields/{field_name}   — Обновить кастомное поле
        DELETE /{project_id}/custom-fields/{field_name}   — Удалить кастомное поле
        POST   /{project_id}/milestones                   — Добавить milestone
        PATCH  /{project_id}/milestones/{milestone_id}    — Обновить milestone
        POST   /{project_id}/milestones/{milestone_id}/change-status — Изменить статус milestone
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project"])

    def _register_routes(self) -> None:
        # --- CRUD ---
        self._router.add_api_route(
            "/", self.create_project, methods=["POST"],
            response_model=SuccessResponse[ProjectResponse], status_code=201,
            summary="Создать проект",
            responses={201: {"description": "Проект создан"}, 403: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/", self.list_projects, methods=["GET"],
            response_model=SuccessResponse[list[ProjectResponse]],
            summary="Список проектов workspace",
        )
        self._router.add_api_route(
            "/archived", self.list_archived_projects, methods=["GET"],
            response_model=SuccessResponse[list[ProjectResponse]],
            summary="Архивированные проекты",
        )
        self._router.add_api_route(
            "/overdue", self.list_overdue_projects, methods=["GET"],
            response_model=SuccessResponse[list[ProjectResponse]],
            summary="Просроченные проекты workspace",
            description="Возвращает просроченные проекты в рамках workspace (требует разрешение).",
            responses={
                200: {"description": "Список просроченных проектов"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Нет доступа", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}", self.get_project, methods=["GET"],
            response_model=SuccessResponse[ProjectResponse],
            summary="Получить проект",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}", self.update_project_info, methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить информацию проекта",
        )

        # --- Lifecycle ---
        self._router.add_api_route(
            "/{project_id}/archive", self.archive_project, methods=["POST"],
            response_model=MessageResponse, summary="Архивировать проект",
        )
        self._router.add_api_route(
            "/{project_id}/restore", self.restore_project, methods=["POST"],
            response_model=MessageResponse, summary="Восстановить проект",
        )
        self._router.add_api_route(
            "/{project_id}/suspend", self.suspend_project, methods=["POST"],
            response_model=MessageResponse, summary="Приостановить проект",
        )
        self._router.add_api_route(
            "/{project_id}/reactivate", self.reactivate_project, methods=["POST"],
            response_model=MessageResponse, summary="Реактивировать проект",
        )
        self._router.add_api_route(
            "/{project_id}/request-deletion", self.request_deletion, methods=["POST"],
            response_model=MessageResponse, summary="Запросить удаление проекта",
        )

        # --- Ownership ---
        self._router.add_api_route(
            "/{project_id}/transfer-ownership", self.transfer_ownership, methods=["POST"],
            response_model=MessageResponse, summary="Передать владение проектом",
        )
        self._router.add_api_route(
            "/{project_id}/owners", self.add_owner, methods=["POST"],
            response_model=MessageResponse, summary="Добавить со-владельца",
        )
        self._router.add_api_route(
            "/{project_id}/owners/{user_id}", self.remove_owner, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить со-владельца",
        )

        # --- Settings ---
        self._router.add_api_route(
            "/{project_id}/methodology", self.change_methodology, methods=["PATCH"],
            response_model=MessageResponse, summary="Сменить методологию",
        )
        self._router.add_api_route(
            "/{project_id}/visibility", self.change_visibility, methods=["PATCH"],
            response_model=MessageResponse, summary="Сменить видимость",
        )

        # --- Custom fields ---
        self._router.add_api_route(
            "/{project_id}/custom-fields", self.add_custom_field, methods=["POST"],
            response_model=MessageResponse, summary="Добавить кастомное поле",
        )
        self._router.add_api_route(
            "/{project_id}/custom-fields/{field_name}", self.update_custom_field, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить кастомное поле",
        )
        self._router.add_api_route(
            "/{project_id}/custom-fields/{field_name}", self.remove_custom_field, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить кастомное поле",
        )

        # --- Milestones ---
        self._router.add_api_route(
            "/{project_id}/milestones", self.add_milestone, methods=["POST"],
            response_model=SuccessResponse[MilestoneResponse], status_code=201,
            summary="Добавить milestone",
        )
        self._router.add_api_route(
            "/{project_id}/milestones/{milestone_id}", self.update_milestone, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить milestone",
        )
        self._router.add_api_route(
            "/{project_id}/milestones/{milestone_id}/change-status", self.change_milestone_status, methods=["POST"],
            response_model=MessageResponse, summary="Изменить статус milestone",
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def create_project(
        self,
        ws_id: str,
        body: CreateProjectRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        membership_repo=Depends(get_project_membership_repository),
        board_repo=Depends(get_board_repository),
        role_repo=Depends(get_project_role_repository),
        identity_port=Depends(get_project_identity_user_port),
        workspace_port=Depends(get_project_workspace_port),
        ws_permission_checker=Depends(get_project_ws_permission_checker_port),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[ProjectResponse]:
        handler = CreateProjectHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            board_repo=board_repo,
            project_role_repo=role_repo,
            identity_port=identity_port,
            workspace_port=workspace_port,
            workspace_permission_checker=ws_permission_checker,
            event_bus=event_bus,
        )
        owner_id = body.owner_id or caller_id
        command = CreateProjectCommand(
            caller_id=caller_id,
            name=body.name,
            workspace_id=ws_id,
            owner_id=owner_id,
            methodology=body.methodology,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ProjectResponse.model_validate(dto.__dict__))

    async def list_projects(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectResponse]]:
        handler = GetProjectsByWorkspaceHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetProjectsByWorkspaceQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        return SuccessResponse(data=items)

    async def list_archived_projects(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectResponse]]:
        handler = GetArchivedProjectsHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetArchivedProjectsQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        return SuccessResponse(data=items)

    async def list_overdue_projects(
        self,
        ws_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectResponse]]:
        handler = GetOverdueProjectsHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetOverdueProjectsQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_project(
        self,
        ws_id: str,
        project_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[ProjectResponse]:
        handler = GetProjectHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetProjectQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ProjectResponse.model_validate(dto.__dict__))

    async def update_project_info(
        self,
        ws_id: str,
        project_id: str,
        body: UpdateProjectInfoRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateProjectInfoHandler(
            project_repo=project_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateProjectInfoCommand(
            caller_id=caller_id,
            project_id=project_id,
            name=body.name,
            description_content=body.description.content if body.description else None,
            description_format=body.description.format if body.description else None,
            icon=body.icon,
            color=body.color,
            category_name=body.category.name if body.category else None,
            category_color=body.category.color if body.category else None,
            start_date=str(body.start_date) if body.start_date else None,
            deadline=str(body.deadline) if body.deadline else None,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Информация проекта обновлена"})

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def archive_project(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ArchiveProjectHandler(
            project_repo=project_repo, sprint_repo=sprint_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ArchiveProjectCommand(caller_id=caller_id, project_id=project_id))
        return SuccessResponse(data={"message": "Проект архивирован"})

    async def restore_project(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RestoreProjectHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RestoreProjectCommand(caller_id=caller_id, project_id=project_id))
        return SuccessResponse(data={"message": "Проект восстановлен"})

    async def suspend_project(
        self, ws_id: str, project_id: str, body: SuspendProjectRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = SuspendProjectHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(SuspendProjectCommand(caller_id=caller_id, project_id=project_id, reason=body.reason))
        return SuccessResponse(data={"message": "Проект приостановлен"})

    async def reactivate_project(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ReactivateProjectHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ReactivateProjectCommand(caller_id=caller_id, project_id=project_id))
        return SuccessResponse(data={"message": "Проект реактивирован"})

    async def request_deletion(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RequestProjectDeletionHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RequestProjectDeletionCommand(caller_id=caller_id, project_id=project_id))
        return SuccessResponse(data={"message": "Запрос на удаление проекта отправлен"})

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    async def transfer_ownership(
        self, ws_id: str, project_id: str, body: TransferProjectOwnershipRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = TransferProjectOwnershipHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(TransferProjectOwnershipCommand(
            caller_id=caller_id, project_id=project_id,
            from_owner_id=body.from_owner_id, to_owner_id=body.to_owner_id,
        ))
        return SuccessResponse(data={"message": "Владение проектом передано"})

    async def add_owner(
        self, ws_id: str, project_id: str, body: AddProjectOwnerRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddProjectOwnerHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddProjectOwnerCommand(caller_id=caller_id, project_id=project_id, user_id=body.user_id))
        return SuccessResponse(data={"message": "Со-владелец добавлен"})

    async def remove_owner(
        self, ws_id: str, project_id: str, user_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveProjectOwnerHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveProjectOwnerCommand(caller_id=caller_id, project_id=project_id, user_id=user_id))
        return SuccessResponse(data={"message": "Со-владелец удалён"})

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    async def change_methodology(
        self, ws_id: str, project_id: str, body: ChangeProjectMethodologyRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeProjectMethodologyHandler(
            project_repo=project_repo, sprint_repo=sprint_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeProjectMethodologyCommand(
            caller_id=caller_id, project_id=project_id, new_methodology=body.new_methodology,
        ))
        return SuccessResponse(data={"message": "Методология изменена"})

    async def change_visibility(
        self, ws_id: str, project_id: str, body: ChangeProjectVisibilityRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeProjectVisibilityHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeProjectVisibilityCommand(
            caller_id=caller_id, project_id=project_id, visibility=body.visibility,
        ))
        return SuccessResponse(data={"message": "Видимость изменена"})

    # ------------------------------------------------------------------
    # Custom fields
    # ------------------------------------------------------------------

    async def add_custom_field(
        self, ws_id: str, project_id: str, body: AddProjectCustomFieldRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddProjectCustomFieldHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddProjectCustomFieldCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, field_type=body.field_type,
            is_required=body.is_required, options=body.options,
            default_value=body.default_value, description=body.description,
        ))
        return SuccessResponse(data={"message": "Кастомное поле добавлено"})

    async def update_custom_field(
        self, ws_id: str, project_id: str, field_name: str, body: UpdateProjectCustomFieldRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateProjectCustomFieldHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateProjectCustomFieldCommand(
            caller_id=caller_id, project_id=project_id, name=field_name,
            new_name=body.new_name, field_type=body.field_type,
            is_required=body.is_required, options=body.options,
            default_value=body.default_value, description=body.description,
        ))
        return SuccessResponse(data={"message": "Кастомное поле обновлено"})

    async def remove_custom_field(
        self, ws_id: str, project_id: str, field_name: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveProjectCustomFieldHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveProjectCustomFieldCommand(
            caller_id=caller_id, project_id=project_id, name=field_name,
        ))
        return SuccessResponse(data={"message": "Кастомное поле удалено"})

    # ------------------------------------------------------------------
    # Milestones
    # ------------------------------------------------------------------

    async def add_milestone(
        self, ws_id: str, project_id: str, body: AddProjectMilestoneRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[MilestoneResponse]:
        handler = AddProjectMilestoneHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        command = AddProjectMilestoneCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, due_date=body.due_date,
            description_content=body.description.content if body.description else None,
            description_format=body.description.format if body.description else None,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=MilestoneResponse.model_validate(dto.__dict__))

    async def update_milestone(
        self, ws_id: str, project_id: str, milestone_id: str, body: UpdateProjectMilestoneRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateProjectMilestoneHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        command = UpdateProjectMilestoneCommand(
            caller_id=caller_id, project_id=project_id, milestone_id=milestone_id,
            name=body.name, due_date=body.due_date,
            description_content=body.description.content if body.description else None,
            description_format=body.description.format if body.description else None,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Milestone обновлён"})

    async def change_milestone_status(
        self, ws_id: str, project_id: str, milestone_id: str, body: ChangeProjectMilestoneStatusRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeProjectMilestoneStatusHandler(
            project_repo=project_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeProjectMilestoneStatusCommand(
            caller_id=caller_id, project_id=project_id,
            milestone_id=milestone_id, new_status=body.new_status,
        ))
        return SuccessResponse(data={"message": "Статус milestone изменён"})
