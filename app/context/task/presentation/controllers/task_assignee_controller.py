from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.task.application.commands.assign_task import (
    AssignTaskCommand,
    AssignTaskHandler,
)
from app.context.task.application.commands.unassign_task import (
    UnassignTaskCommand,
    UnassignTaskHandler,
)
from app.context.task.application.commands.assign_task_to_sprint import (
    AssignTaskToSprintCommand,
    AssignTaskToSprintHandler,
)
from app.context.task.application.commands.remove_task_from_sprint import (
    RemoveTaskFromSprintCommand,
    RemoveTaskFromSprintHandler,
)
from app.context.task.application.commands.assign_task_to_epic import (
    AssignTaskToEpicCommand,
    AssignTaskToEpicHandler,
)
from app.context.task.application.commands.remove_task_from_epic import (
    RemoveTaskFromEpicCommand,
    RemoveTaskFromEpicHandler,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_changelog_repository,
    get_task_epic_port,
    get_task_event_bus,
    get_task_identity_user_port,
    get_task_permission_checker,
    get_task_project_membership_port,
    get_task_repository,
    get_task_sprint_port,
)
from app.context.task.presentation.schemas.requests.assign_task_request import AssignTaskRequest
from app.context.task.presentation.schemas.requests.assign_task_to_sprint_request import AssignTaskToSprintRequest
from app.context.task.presentation.schemas.requests.assign_task_to_epic_request import AssignTaskToEpicRequest


class TaskAssigneeController(BaseController):
    """
    Контроллер исполнителей, спринтов и эпиков задачи.

    Endpoint'ы:
        POST   /{task_id}/assignees                    — Назначить исполнителя
        DELETE /{task_id}/assignees/{assignee_id}      — Снять исполнителя
        POST   /{task_id}/sprint                       — Привязать к спринту
        DELETE /{task_id}/sprint                       — Убрать из спринта
        POST   /{task_id}/epic                         — Привязать к эпику
        DELETE /{task_id}/epic                         — Убрать из эпика
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / Assignees & Links"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}/assignees",
            self.assign_task,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Назначить исполнителя",
            description="Назначает исполнителя на задачу.",
            responses={
                200: {"description": "Исполнитель назначен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/assignees/{assignee_id}",
            self.unassign_task,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Снять исполнителя",
            description="Снимает исполнителя с задачи.",
            responses={
                200: {"description": "Исполнитель снят"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/sprint",
            self.assign_to_sprint,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Привязать задачу к спринту",
            description="Привязывает задачу к указанному спринту.",
            responses={
                200: {"description": "Задача привязана к спринту"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/sprint",
            self.remove_from_sprint,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Убрать задачу из спринта",
            description="Убирает задачу из спринта.",
            responses={
                200: {"description": "Задача убрана из спринта"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/epic",
            self.assign_to_epic,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Привязать задачу к эпику",
            description="Привязывает задачу к указанному эпику.",
            responses={
                200: {"description": "Задача привязана к эпику"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/epic",
            self.remove_from_epic,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Убрать задачу из эпика",
            description="Убирает задачу из эпика.",
            responses={
                200: {"description": "Задача убрана из эпика"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )

    async def assign_task(
        self,
        task_id: str,
        body: AssignTaskRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        identity_port=Depends(get_task_identity_user_port),
        membership_port=Depends(get_task_project_membership_port),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Назначить исполнителя."""
        handler = AssignTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            identity_port=identity_port,
            membership_port=membership_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AssignTaskCommand(
            task_id=task_id,
            assignee_id=body.assignee_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Исполнитель назначен"))

    async def unassign_task(
        self,
        task_id: str,
        assignee_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Снять исполнителя."""
        handler = UnassignTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UnassignTaskCommand(
            task_id=task_id,
            assignee_id=assignee_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Исполнитель снят"))

    async def assign_to_sprint(
        self,
        task_id: str,
        body: AssignTaskToSprintRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        sprint_port=Depends(get_task_sprint_port),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Привязать задачу к спринту."""
        handler = AssignTaskToSprintHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            sprint_port=sprint_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AssignTaskToSprintCommand(
            task_id=task_id,
            sprint_id=body.sprint_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача привязана к спринту"))

    async def remove_from_sprint(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Убрать задачу из спринта."""
        handler = RemoveTaskFromSprintHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskFromSprintCommand(
            caller_id=caller_id,
            task_id=task_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача убрана из спринта"))

    async def assign_to_epic(
        self,
        task_id: str,
        body: AssignTaskToEpicRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        epic_port=Depends(get_task_epic_port),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Привязать задачу к эпику."""
        handler = AssignTaskToEpicHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            epic_port=epic_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AssignTaskToEpicCommand(
            task_id=task_id,
            epic_id=body.epic_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача привязана к эпику"))

    async def remove_from_epic(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Убрать задачу из эпика."""
        handler = RemoveTaskFromEpicHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskFromEpicCommand(
            caller_id=caller_id,
            task_id=task_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача убрана из эпика"))
