from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.add_board_column import (
    AddBoardColumnCommand,
    AddBoardColumnHandler,
)
from app.context.project.application.commands.remove_board_column import (
    RemoveBoardColumnCommand,
    RemoveBoardColumnHandler,
)
from app.context.project.application.commands.reorder_board_columns import (
    ReorderBoardColumnsCommand,
    ReorderBoardColumnsHandler,
)
from app.context.project.application.commands.change_board_column_wip_limit import (
    ChangeBoardColumnWipLimitCommand,
    ChangeBoardColumnWipLimitHandler,
)
from app.context.project.application.commands.add_board_swimlane import (
    AddBoardSwimlaneCommand,
    AddBoardSwimlaneHandler,
)
from app.context.project.application.commands.remove_board_swimlane import (
    RemoveBoardSwimlaneCommand,
    RemoveBoardSwimlaneHandler,
)
from app.context.project.application.commands.add_workflow_status import (
    AddWorkflowStatusCommand,
    AddWorkflowStatusHandler,
)
from app.context.project.application.commands.remove_workflow_status import (
    RemoveWorkflowStatusCommand,
    RemoveWorkflowStatusHandler,
)
from app.context.project.application.commands.add_workflow_transition import (
    AddWorkflowTransitionCommand,
    AddWorkflowTransitionHandler,
)
from app.context.project.application.commands.remove_workflow_transition import (
    RemoveWorkflowTransitionCommand,
    RemoveWorkflowTransitionHandler,
)
from app.context.project.application.commands.update_project_view import (
    UpdateProjectViewCommand,
    UpdateProjectViewHandler,
)
from app.context.project.application.commands.delete_project_view import (
    DeleteProjectViewCommand,
    DeleteProjectViewHandler,
)
from app.context.project.application.commands.update_automation_rule import (
    UpdateAutomationRuleCommand,
    UpdateAutomationRuleHandler,
)
from app.context.project.application.commands.remove_automation_rule import (
    RemoveAutomationRuleCommand,
    RemoveAutomationRuleHandler,
)
from app.context.project.application.queries.get_board import (
    GetBoardHandler,
    GetBoardQuery,
)
from app.context.project.presentation.dependencies import (
    get_board_repository,
    get_current_user_id,
    get_project_event_bus,
    get_project_permission_checker,
)
from app.context.project.presentation.schemas.requests.add_board_column_request import (
    AddBoardColumnRequest,
)
from app.context.project.presentation.schemas.requests.change_board_column_wip_limit_request import (
    ChangeBoardColumnWipLimitRequest,
)
from app.context.project.presentation.schemas.requests.reorder_board_columns_request import (
    ReorderBoardColumnsRequest,
)
from app.context.project.presentation.schemas.requests.add_board_swimlane_request import (
    AddBoardSwimlaneRequest,
)
from app.context.project.presentation.schemas.requests.add_workflow_status_request import (
    AddWorkflowStatusRequest,
)
from app.context.project.presentation.schemas.requests.add_workflow_transition_request import (
    AddWorkflowTransitionRequest,
)
from app.context.project.presentation.schemas.requests.update_project_view_request import (
    UpdateProjectViewRequest,
)
from app.context.project.presentation.schemas.requests.update_automation_rule_request import (
    UpdateAutomationRuleRequest,
)
from app.context.project.presentation.schemas.responses.board_response import (
    BoardResponse,
)


class ProjectBoardController(BaseController):
    """
    Контроллер доски проекта (board, columns, swimlanes, workflow, views, automations).

    Endpoint'ы:
        GET    /{project_id}/board                                    — Получить доску
        POST   /{project_id}/board/columns                           — Добавить колонку
        DELETE /{project_id}/board/columns/{column_id}               — Удалить колонку
        PUT    /{project_id}/board/columns/reorder                    — Переупорядочить колонки
        PATCH  /{project_id}/board/columns/{column_id}/wip-limit     — Изменить WIP-лимит
        POST   /{project_id}/board/swimlanes                         — Добавить swimlane
        DELETE /{project_id}/board/swimlanes/{swimlane_id}           — Удалить swimlane
        POST   /{project_id}/board/workflow/statuses                 — Добавить статус
        DELETE /{project_id}/board/workflow/statuses/{status_id}     — Удалить статус
        POST   /{project_id}/board/workflow/transitions              — Добавить переход
        DELETE /{project_id}/board/workflow/transitions/{transition_id} — Удалить переход
        PATCH  /{project_id}/board/views/{view_id}                   — Обновить представление
        DELETE /{project_id}/board/views/{view_id}                   — Удалить представление
        PATCH  /{project_id}/board/automations/{rule_id}             — Обновить правило
        DELETE /{project_id}/board/automations/{rule_id}             — Удалить правило
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project / Board"])

    def _register_routes(self) -> None:
        # Board
        self._router.add_api_route(
            "/{project_id}/board", self.get_board, methods=["GET"],
            response_model=SuccessResponse[BoardResponse],
            summary="Получить доску проекта",
            responses={404: {"model": ErrorResponse}},
        )

        # Columns
        self._router.add_api_route(
            "/{project_id}/board/columns", self.add_column, methods=["POST"],
            response_model=MessageResponse, status_code=201,
            summary="Добавить колонку",
        )
        self._router.add_api_route(
            "/{project_id}/board/columns/{column_id}", self.remove_column, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить колонку",
        )
        self._router.add_api_route(
            "/{project_id}/board/columns/reorder", self.reorder_columns, methods=["PUT"],
            response_model=MessageResponse, summary="Переупорядочить колонки",
        )
        self._router.add_api_route(
            "/{project_id}/board/columns/{column_id}/wip-limit", self.change_wip_limit, methods=["PATCH"],
            response_model=MessageResponse, summary="Изменить WIP-лимит колонки",
        )

        # Swimlanes
        self._router.add_api_route(
            "/{project_id}/board/swimlanes", self.add_swimlane, methods=["POST"],
            response_model=MessageResponse, status_code=201,
            summary="Добавить swimlane",
        )
        self._router.add_api_route(
            "/{project_id}/board/swimlanes/{swimlane_id}", self.remove_swimlane, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить swimlane",
        )

        # Workflow statuses
        self._router.add_api_route(
            "/{project_id}/board/workflow/statuses", self.add_workflow_status, methods=["POST"],
            response_model=MessageResponse, status_code=201,
            summary="Добавить статус workflow",
        )
        self._router.add_api_route(
            "/{project_id}/board/workflow/statuses/{status_id}", self.remove_workflow_status, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить статус workflow",
        )

        # Workflow transitions
        self._router.add_api_route(
            "/{project_id}/board/workflow/transitions", self.add_workflow_transition, methods=["POST"],
            response_model=MessageResponse, status_code=201,
            summary="Добавить переход workflow",
        )
        self._router.add_api_route(
            "/{project_id}/board/workflow/transitions/{transition_id}", self.remove_workflow_transition, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить переход workflow",
        )

        # Views
        self._router.add_api_route(
            "/{project_id}/board/views/{view_id}", self.update_view, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить представление",
        )
        self._router.add_api_route(
            "/{project_id}/board/views/{view_id}", self.delete_view, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить представление",
        )

        # Automations
        self._router.add_api_route(
            "/{project_id}/board/automations/{rule_id}", self.update_automation_rule, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить правило автоматизации",
        )
        self._router.add_api_route(
            "/{project_id}/board/automations/{rule_id}", self.remove_automation_rule, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить правило автоматизации",
        )

    # ------------------------------------------------------------------
    # Board
    # ------------------------------------------------------------------

    async def get_board(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[BoardResponse]:
        handler = GetBoardHandler(board_repo=board_repo, permission_checker=permission_checker)
        query = GetBoardQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=BoardResponse.model_validate(dto.__dict__))

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    async def add_column(
        self, ws_id: str, project_id: str, body: AddBoardColumnRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddBoardColumnHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddBoardColumnCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, color=body.color,
            wip_limit=body.wip_limit, status_mapping_id=body.status_mapping,
        ))
        return SuccessResponse(data={"message": "Колонка добавлена"})

    async def remove_column(
        self, ws_id: str, project_id: str, column_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveBoardColumnHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveBoardColumnCommand(
            caller_id=caller_id, project_id=project_id, column_id=column_id,
        ))
        return SuccessResponse(data={"message": "Колонка удалена"})

    async def reorder_columns(
        self, ws_id: str, project_id: str, body: ReorderBoardColumnsRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ReorderBoardColumnsHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ReorderBoardColumnsCommand(
            caller_id=caller_id, project_id=project_id, column_ids=body.column_ids,
        ))
        return SuccessResponse(data={"message": "Колонки переупорядочены"})

    async def change_wip_limit(
        self, ws_id: str, project_id: str, column_id: str, body: ChangeBoardColumnWipLimitRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeBoardColumnWipLimitHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeBoardColumnWipLimitCommand(
            caller_id=caller_id, project_id=project_id,
            column_id=column_id, wip_limit=body.wip_limit,
        ))
        return SuccessResponse(data={"message": "WIP-лимит изменён"})

    # ------------------------------------------------------------------
    # Swimlanes
    # ------------------------------------------------------------------

    async def add_swimlane(
        self, ws_id: str, project_id: str, body: AddBoardSwimlaneRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddBoardSwimlaneHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddBoardSwimlaneCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, group_by=body.group_by, group_value=body.group_value,
        ))
        return SuccessResponse(data={"message": "Swimlane добавлена"})

    async def remove_swimlane(
        self, ws_id: str, project_id: str, swimlane_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveBoardSwimlaneHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveBoardSwimlaneCommand(
            caller_id=caller_id, project_id=project_id, swimlane_id=swimlane_id,
        ))
        return SuccessResponse(data={"message": "Swimlane удалена"})

    # ------------------------------------------------------------------
    # Workflow statuses
    # ------------------------------------------------------------------

    async def add_workflow_status(
        self, ws_id: str, project_id: str, body: AddWorkflowStatusRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddWorkflowStatusHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddWorkflowStatusCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, category=body.category,
            color=body.color, icon=body.icon, is_default=body.is_default,
        ))
        return SuccessResponse(data={"message": "Статус workflow добавлен"})

    async def remove_workflow_status(
        self, ws_id: str, project_id: str, status_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveWorkflowStatusHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveWorkflowStatusCommand(
            caller_id=caller_id, project_id=project_id, status_id=status_id,
        ))
        return SuccessResponse(data={"message": "Статус workflow удалён"})

    # ------------------------------------------------------------------
    # Workflow transitions
    # ------------------------------------------------------------------

    async def add_workflow_transition(
        self, ws_id: str, project_id: str, body: AddWorkflowTransitionRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddWorkflowTransitionHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddWorkflowTransitionCommand(
            caller_id=caller_id, project_id=project_id,
            from_status_id=body.from_status_id, to_status_id=body.to_status_id,
            name=body.name, required_permission=body.required_permission,
        ))
        return SuccessResponse(data={"message": "Переход workflow добавлен"})

    async def remove_workflow_transition(
        self, ws_id: str, project_id: str, transition_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveWorkflowTransitionHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveWorkflowTransitionCommand(
            caller_id=caller_id, project_id=project_id, transition_id=transition_id,
        ))
        return SuccessResponse(data={"message": "Переход workflow удалён"})

    # ------------------------------------------------------------------
    # Views
    # ------------------------------------------------------------------

    async def update_view(
        self, ws_id: str, project_id: str, view_id: str, body: UpdateProjectViewRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateProjectViewHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateProjectViewCommand(
            caller_id=caller_id, project_id=project_id,
            view_id=view_id, name=body.name, view_type=body.view_type,
        ))
        return SuccessResponse(data={"message": "Представление обновлено"})

    async def delete_view(
        self, ws_id: str, project_id: str, view_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = DeleteProjectViewHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(DeleteProjectViewCommand(
            caller_id=caller_id, project_id=project_id, view_id=view_id,
        ))
        return SuccessResponse(data={"message": "Представление удалено"})

    # ------------------------------------------------------------------
    # Automations
    # ------------------------------------------------------------------

    async def update_automation_rule(
        self, ws_id: str, project_id: str, rule_id: str, body: UpdateAutomationRuleRequest,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateAutomationRuleHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateAutomationRuleCommand(
            caller_id=caller_id, project_id=project_id,
            rule_id=rule_id, is_enabled=body.is_enabled, action_params=body.action_params,
        ))
        return SuccessResponse(data={"message": "Правило автоматизации обновлено"})

    async def remove_automation_rule(
        self, ws_id: str, project_id: str, rule_id: str,
        caller_id: str = Depends(get_current_user_id),
        board_repo=Depends(get_board_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveAutomationRuleHandler(
            board_repo=board_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveAutomationRuleCommand(
            caller_id=caller_id, project_id=project_id, rule_id=rule_id,
        ))
        return SuccessResponse(data={"message": "Правило автоматизации удалено"})
