from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.create_department import (
    CreateDepartmentCommand,
    CreateDepartmentHandler,
)
from app.context.organization.application.commands.update_department import (
    UpdateDepartmentCommand,
    UpdateDepartmentHandler,
)
from app.context.organization.application.commands.delete_department import (
    DeleteDepartmentCommand,
    DeleteDepartmentHandler,
)
from app.context.organization.application.commands.add_department_member import (
    AddDepartmentMemberCommand,
    AddDepartmentMemberHandler,
)
from app.context.organization.application.commands.remove_department_member import (
    RemoveDepartmentMemberCommand,
    RemoveDepartmentMemberHandler,
)
from app.context.organization.application.queries.get_departments_by_org import (
    GetDepartmentsByOrgHandler,
    GetDepartmentsByOrgQuery,
)
from app.context.organization.application.queries.get_department import (
    GetDepartmentHandler,
    GetDepartmentQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_department_repository,
    get_org_membership_repository,
    get_org_permission_checker,
    get_organization_event_bus,
    get_organization_repository,
)
from app.context.organization.presentation.schemas.requests.create_department_request import (
    CreateDepartmentRequest,
)
from app.context.organization.presentation.schemas.requests.update_department_request import (
    UpdateDepartmentRequest,
)
from app.context.organization.presentation.schemas.responses.department_response import (
    DepartmentResponse,
)


class DepartmentController(BaseController):
    """
    Контроллер подразделений организации.

    Endpoint'ы:
        GET    /{org_id}/departments                                    — Список подразделений
        GET    /{org_id}/departments/{department_id}                    — Получить подразделение
        POST   /{org_id}/departments                                    — Создать подразделение
        PATCH  /{org_id}/departments/{department_id}                    — Обновить подразделение
        DELETE /{org_id}/departments/{department_id}                    — Удалить подразделение
        POST   /{org_id}/departments/{department_id}/members/{user_id}  — Добавить участника
        DELETE /{org_id}/departments/{department_id}/members/{user_id}  — Удалить участника
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Departments"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/departments",
            self.get_departments,
            methods=["GET"],
            response_model=SuccessResponse[list[DepartmentResponse]],
            summary="Список подразделений",
            description="Возвращает список подразделений организации.",
            responses={
                200: {"description": "Список подразделений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments/{department_id}",
            self.get_department,
            methods=["GET"],
            response_model=SuccessResponse[DepartmentResponse],
            summary="Получить подразделение",
            description="Возвращает данные подразделения по UUID.",
            responses={
                200: {"description": "Данные подразделения"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Подразделение не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments",
            self.create_department,
            methods=["POST"],
            response_model=SuccessResponse[DepartmentResponse],
            status_code=201,
            summary="Создать подразделение",
            description="Создаёт новое подразделение в организации.",
            responses={
                201: {"description": "Подразделение создано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments/{department_id}",
            self.update_department,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить подразделение",
            description="Обновляет название и/или руководителя подразделения.",
            responses={
                200: {"description": "Подразделение обновлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Подразделение не найдено", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments/{department_id}",
            self.delete_department,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить подразделение",
            description="Деактивирует подразделение (мягкое удаление).",
            responses={
                200: {"description": "Подразделение удалено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Подразделение не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments/{department_id}/members/{user_id}",
            self.add_department_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить участника в подразделение",
            description="Добавляет участника организации в подразделение. Пользователь должен быть членом организации.",
            responses={
                200: {"description": "Участник добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Подразделение не найдено / пользователь не в организации", "model": ErrorResponse},
                409: {"description": "Участник уже в подразделении", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/departments/{department_id}/members/{user_id}",
            self.remove_department_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника из подразделения",
            description="Удаляет участника из подразделения.",
            responses={
                200: {"description": "Участник удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Подразделение не найдено", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Department CRUD
    # ------------------------------------------------------------------

    async def get_departments(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[list[DepartmentResponse]]:
        """Получить список подразделений."""
        handler = GetDepartmentsByOrgHandler(department_repo=department_repo, org_repo=org_repo, org_permission_checker=org_permission_checker)
        query = GetDepartmentsByOrgQuery(caller_id=caller_id, org_id=org_id)
        dto = await handler.handle(query)
        items = [DepartmentResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_department(
        self,
        org_id: str,
        department_id: str,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[DepartmentResponse]:
        """Получить подразделение по ID."""
        handler = GetDepartmentHandler(department_repo=department_repo, org_permission_checker=org_permission_checker)
        query = GetDepartmentQuery(caller_id=caller_id, org_id=org_id, department_id=department_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=DepartmentResponse.model_validate(dto.model_dump()))

    async def create_department(
        self,
        org_id: str,
        body: CreateDepartmentRequest,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[DepartmentResponse]:
        """Создать подразделение."""
        handler = CreateDepartmentHandler(
            department_repo=department_repo,
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = CreateDepartmentCommand(
            caller_id=caller_id,
            org_id=org_id,
            name=body.name,
            parent_id=body.parent_id,
            lead_id=body.lead_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DepartmentResponse.model_validate(dto.model_dump()))

    async def update_department(
        self,
        org_id: str,
        department_id: str,
        body: UpdateDepartmentRequest,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить подразделение."""
        handler = UpdateDepartmentHandler(
            department_repo=department_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateDepartmentCommand(
            caller_id=caller_id,
            org_id=org_id,
            department_id=department_id,
            name=body.name,
            lead_id=body.lead_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Подразделение обновлено")

    async def delete_department(
        self,
        org_id: str,
        department_id: str,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить подразделение."""
        handler = DeleteDepartmentHandler(
            department_repo=department_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = DeleteDepartmentCommand(
            caller_id=caller_id,
            org_id=org_id,
            department_id=department_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Подразделение удалено")

    # ------------------------------------------------------------------
    # Department members
    # ------------------------------------------------------------------

    async def add_department_member(
        self,
        org_id: str,
        department_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Добавить участника в подразделение."""
        handler = AddDepartmentMemberHandler(
            department_repo=department_repo,
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddDepartmentMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            department_id=department_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник добавлен в подразделение")

    async def remove_department_member(
        self,
        org_id: str,
        department_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        department_repo=Depends(get_department_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить участника из подразделения."""
        handler = RemoveDepartmentMemberHandler(
            department_repo=department_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RemoveDepartmentMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            department_id=department_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник удалён из подразделения")
