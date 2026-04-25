from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.queries.get_workspaces_by_organization import (
    GetWorkspacesByOrganizationHandler,
    GetWorkspacesByOrganizationQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_repository,
    get_ws_org_permission_checker_port,
    get_ws_organization_membership_port,
)
from app.context.workspace.presentation.schemas.responses.workspace_response import WorkspaceResponse


class OrgWorkspaceController(BaseController):
    """
    Контроллер workspace организации (read-only).

    Endpoint'ы:
        GET    /{org_id}/workspaces    — Список workspace организации
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Workspaces"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/workspaces",
            self.get_workspaces_by_organization,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceResponse],
            summary="Список workspace организации",
            description=(
                "Возвращает список workspace организации. "
                "Если у пользователя есть орг-разрешение `workspaces.read` — все workspace организации, "
                "иначе — только те, где пользователь является участником."
            ),
            responses={
                200: {"description": "Список workspace организации"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Не является членом организации", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Organization Workspaces (read-only)
    # ------------------------------------------------------------------

    async def get_workspaces_by_organization(
        self,
        org_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        org_membership_port=Depends(get_ws_organization_membership_port),
        org_permission_checker=Depends(get_ws_org_permission_checker_port),
    ) -> PaginatedResponse[WorkspaceResponse]:
        """Список workspace организации."""
        handler = GetWorkspacesByOrganizationHandler(
            ws_repo=ws_repo,
            org_membership_port=org_membership_port,
            org_permission_checker=org_permission_checker,
        )
        query = GetWorkspacesByOrganizationQuery(
            caller_id=caller_id,
            organization_id=org_id,
        )
        dto = await handler.handle(query)
        items = [WorkspaceResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)
