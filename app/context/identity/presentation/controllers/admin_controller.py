from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.identity.application.commands.assign_role import (
    AssignRoleCommand,
    AssignRoleHandler,
)
from app.context.identity.application.commands.remove_role import (
    RemoveRoleCommand,
    RemoveRoleHandler,
)
from app.context.identity.application.commands.unlock_account import (
    UnlockAccountCommand,
    UnlockAccountHandler,
)
from app.context.identity.presentation.dependencies import (
    get_current_user_id,
    get_identity_event_bus,
    get_permission_checker,
    get_role_repository,
    get_user_auth_repository,
    get_user_repository,
)


class AdminController(BaseController):
    """
    Контроллер администрирования Identity BC.

    Endpoint'ы:
        POST   /admin/users/{user_id}/roles/{role_id}  — Назначить роль пользователю
        DELETE /admin/users/{user_id}/roles/{role_id}  — Снять роль с пользователя
        POST   /admin/users/{user_id}/unlock            — Разблокировать пользователя
    """

    def __init__(self) -> None:
        super().__init__(prefix="/admin/users", tags=["Identity / Admin"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{user_id}/roles/{role_id}",
            self.assign_role,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Назначить роль пользователю",
            description=(
                "Назначает указанную роль пользователю. "
                "Проверяет существование пользователя и роли. "
                "Если роль уже назначена — возвращает ошибку 409."
            ),
            responses={
                200: {"description": "Роль назначена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Пользователь или роль не найдены", "model": ErrorResponse},
                409: {"description": "Роль уже назначена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{user_id}/roles/{role_id}",
            self.remove_role,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Снять роль с пользователя",
            description=(
                "Снимает указанную роль с пользователя. "
                "Нельзя снять последнюю системную роль."
            ),
            responses={
                200: {"description": "Роль снята"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Пользователь или роль не найдены", "model": ErrorResponse},
                409: {"description": "Нельзя снять последнюю системную роль", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{user_id}/unlock",
            self.unlock_account,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Разблокировать пользователя",
            description=(
                "Сбрасывает блокировку аккаунта, вызванную неудачными "
                "попытками входа. Административная операция."
            ),
            responses={
                200: {"description": "Аккаунт разблокирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        current_user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        role_repo=Depends(get_role_repository),
        event_bus=Depends(get_identity_event_bus),
        permission_checker=Depends(get_permission_checker),
    ) -> MessageResponse:
        """Назначить роль пользователю."""
        handler = AssignRoleHandler(
            user_repo=user_repo,
            role_repo=role_repo,
            event_bus=event_bus,
            permission_checker=permission_checker,
        )
        command = AssignRoleCommand(
            caller_id=current_user_id,
            user_id=user_id,
            role_id=role_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Роль назначена"})

    async def remove_role(
        self,
        user_id: str,
        role_id: str,
        current_user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        role_repo=Depends(get_role_repository),
        event_bus=Depends(get_identity_event_bus),
        permission_checker=Depends(get_permission_checker),
    ) -> MessageResponse:
        """Снять роль с пользователя."""
        handler = RemoveRoleHandler(
            user_repo=user_repo,
            role_repo=role_repo,
            event_bus=event_bus,
            permission_checker=permission_checker,
        )
        command = RemoveRoleCommand(
            caller_id=current_user_id,
            user_id=user_id,
            role_id=role_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Роль снята"})

    # ------------------------------------------------------------------
    # Account unlock
    # ------------------------------------------------------------------

    async def unlock_account(
        self,
        user_id: str,
        current_user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        permission_checker=Depends(get_permission_checker),
    ) -> MessageResponse:
        """Разблокировать пользователя."""
        handler = UnlockAccountHandler(
            user_auth_repo=user_auth_repo,
            permission_checker=permission_checker,
        )
        command = UnlockAccountCommand(
            caller_id=current_user_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Аккаунт разблокирован"})
