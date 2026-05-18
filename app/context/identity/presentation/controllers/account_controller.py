from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.identity.application.commands.cancel_account_deletion import (
    CancelAccountDeletionCommand,
    CancelAccountDeletionHandler,
)
from app.context.identity.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordHandler,
)
from app.context.identity.application.commands.disable_account import (
    DisableAccountCommand,
    DisableAccountHandler,
)
from app.context.identity.application.commands.reactivate_account import (
    ReactivateAccountCommand,
    ReactivateAccountHandler,
)
from app.context.identity.application.commands.request_account_deletion import (
    RequestAccountDeletionCommand,
    RequestAccountDeletionHandler,
)
from app.context.identity.application.commands.terminate_all_sessions import (
    TerminateAllSessionsCommand,
    TerminateAllSessionsHandler,
)
from app.context.identity.application.commands.terminate_session import (
    TerminateSessionCommand,
    TerminateSessionHandler,
)
from app.context.identity.application.queries.get_active_sessions import (
    GetActiveSessionsHandler,
    GetActiveSessionsQuery,
)
from app.context.identity.application.queries.get_role_by_id import (
    GetRoleByIdHandler,
    GetRoleByIdQuery,
)
from app.context.identity.application.queries.get_roles import (
    GetRolesHandler,
    GetRolesQuery,
)
from app.context.identity.application.queries.get_user_by_id import (
    GetUserByIdHandler,
    GetUserByIdQuery,
)
from app.context.identity.presentation.dependencies import (
    get_current_user_id,
    get_identity_event_bus,
    get_identity_notification_port,
    get_password_port,
    get_role_repository,
    get_session_repository,
    get_user_auth_repository,
    get_user_repository,
)
from app.context.identity.presentation.schemas.requests.change_password_request import (
    ChangePasswordRequest,
)
from app.context.identity.presentation.schemas.requests.terminate_all_sessions_request import (
    TerminateAllSessionsRequest,
)
from app.context.identity.presentation.schemas.responses.role_response import RoleResponse
from app.context.identity.presentation.schemas.responses.session_response import SessionResponse
from app.context.identity.presentation.schemas.responses.terminate_all_sessions_response import (
    TerminateAllSessionsResponse,
)
from app.context.identity.presentation.schemas.responses.user_response import UserResponse


class AccountController(BaseController):
    """
    Контроллер аккаунта Identity BC.

    Endpoint'ы:
        GET    /account/me                        — Текущий пользователь
        POST   /account/me/change-password        — Смена пароля
        POST   /account/me/request-deletion       — Запрос удаления аккаунта
        POST   /account/me/cancel-deletion        — Отмена удаления аккаунта
        POST   /account/me/disable                — Деактивация аккаунта
        POST   /account/me/reactivate             — Реактивация аккаунта
        GET    /account/sessions                  — Активные сессии
        DELETE /account/sessions/{session_id}     — Завершить одну сессию
        DELETE /account/sessions                  — Завершить все сессии кроме текущей
        GET    /account/roles                     — Список ролей
        GET    /account/roles/{role_id}           — Получить роль по ID
    """

    def __init__(self) -> None:
        super().__init__(prefix="/account", tags=["Identity / Account"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/me",
            self.get_me,
            methods=["GET"],
            response_model=SuccessResponse[UserResponse],
            summary="Получить текущего пользователя",
            description=(
                "Возвращает данные аутентифицированного пользователя. "
                "Идентификация выполняется по JWT access-токену."
            ),
            responses={
                200: {"description": "Данные пользователя"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/users/{user_id}",
            self.get_user_by_id,
            methods=["GET"],
            response_model=SuccessResponse[UserResponse],
            summary="Получить пользователя по ID",
            description=(
                "Возвращает базовые данные пользователя (id, email, status) по UUID. "
                "Доступно любому авторизованному пользователю — используется UI для "
                "отображения имени/email коллег по задачам и комментариям."
            ),
            responses={
                200: {"description": "Данные пользователя"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/change-password",
            self.change_password,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Смена пароля",
            description=(
                "Меняет пароль текущего пользователя. "
                "Требует указания текущего пароля для подтверждения."
            ),
            responses={
                200: {"description": "Пароль изменён"},
                401: {"description": "Не аутентифицирован или неверный текущий пароль", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/request-deletion",
            self.request_account_deletion,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Запрос удаления аккаунта",
            description=(
                "Инициирует процесс удаления аккаунта. "
                "Статус аккаунта меняется на `pending_deletion`. "
                "Можно отменить через эндпоинт cancel-deletion."
            ),
            responses={
                200: {"description": "Запрос удаления принят"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/cancel-deletion",
            self.cancel_account_deletion,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отмена удаления аккаунта",
            description=(
                "Отменяет ранее запрошенное удаление аккаунта. "
                "Статус возвращается в `active`."
            ),
            responses={
                200: {"description": "Удаление отменено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Аккаунт не в статусе pending_deletion", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/disable",
            self.disable_account,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивация аккаунта",
            description=(
                "Деактивирует аккаунт текущего пользователя. "
                "Статус меняется на `disabled`. "
                "Для восстановления используйте эндпоинт reactivate."
            ),
            responses={
                200: {"description": "Аккаунт деактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/reactivate",
            self.reactivate_account,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивация аккаунта",
            description=(
                "Реактивирует деактивированный аккаунт. "
                "Статус возвращается в `active`."
            ),
            responses={
                200: {"description": "Аккаунт реактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Аккаунт не в статусе disabled", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/sessions",
            self.get_sessions,
            methods=["GET"],
            response_model=SuccessResponse[list[SessionResponse]],
            summary="Активные сессии пользователя",
            description=(
                "Возвращает список всех активных сессий текущего пользователя. "
                "Каждая сессия содержит информацию об устройстве, IP-адресе "
                "и времени создания/истечения."
            ),
            responses={
                200: {"description": "Список активных сессий"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/sessions/{session_id}",
            self.terminate_session,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Завершить одну сессию",
            description=(
                "Завершает указанную сессию текущего пользователя. "
                "Проверяет, что сессия принадлежит аутентифицированному пользователю. "
                "Завершённая сессия получает статус `terminated`."
            ),
            responses={
                200: {"description": "Сессия завершена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Сессия не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/sessions",
            self.terminate_all_sessions,
            methods=["DELETE"],
            response_model=SuccessResponse[TerminateAllSessionsResponse],
            summary="Завершить все сессии кроме текущей",
            description=(
                "Завершает все активные сессии текущего пользователя, "
                "кроме сессии, указанной в `current_session_id`. "
                "Возвращает количество завершённых сессий."
            ),
            responses={
                200: {"description": "Сессии завершены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/roles",
            self.get_roles,
            methods=["GET"],
            response_model=SuccessResponse[list[RoleResponse]],
            summary="Список ролей",
            description=(
                "Возвращает список ролей в системе. "
                "Поддерживает фильтрацию по имени и пагинацию через offset/limit."
            ),
            responses={
                200: {"description": "Список ролей"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/roles/{role_id}",
            self.get_role,
            methods=["GET"],
            response_model=SuccessResponse[RoleResponse],
            summary="Получить роль по ID",
            description=(
                "Возвращает данные конкретной роли по её UUID. "
                "Включает название, список разрешений и признак системной роли."
            ),
            responses={
                200: {"description": "Данные роли"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------

    async def get_me(
        self,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
    ) -> SuccessResponse[UserResponse]:
        """Получить текущего пользователя."""
        handler = GetUserByIdHandler(user_repo=user_repo)
        query = GetUserByIdQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=UserResponse.model_validate(dto.model_dump()))

    async def get_user_by_id(
        self,
        user_id: str,
        _: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
    ) -> SuccessResponse[UserResponse]:
        """
        Получить пользователя по UUID.

        Доступно любому авторизованному пользователю — используется UI для
        отображения email/имени коллег рядом с UUID assignee/author. Возвращает
        тот же `UserResponse`, что и `/account/me`. Не раскрывает приватные
        данные (пароль, 2FA-секреты и т.п. — их нет в `UserDTO`).
        """
        handler = GetUserByIdHandler(user_repo=user_repo)
        query = GetUserByIdQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=UserResponse.model_validate(dto.model_dump()))

    async def change_password(
        self,
        body: ChangePasswordRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        password_port=Depends(get_password_port),
        event_bus=Depends(get_identity_event_bus),
        notification_port=Depends(get_identity_notification_port),
    ) -> MessageResponse:
        """Смена пароля."""
        handler = ChangePasswordHandler(
            user_auth_repo=user_auth_repo,
            password_port=password_port,
            event_bus=event_bus,
            notification_port=notification_port,
        )
        command = ChangePasswordCommand(
            user_id=user_id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Пароль успешно изменён"})

    async def request_account_deletion(
        self,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Запрос удаления аккаунта."""
        handler = RequestAccountDeletionHandler(
            user_repo=user_repo,
            event_bus=event_bus,
        )
        command = RequestAccountDeletionCommand(user_id=user_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Запрос на удаление аккаунта принят"})

    async def cancel_account_deletion(
        self,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
    ) -> MessageResponse:
        """Отмена удаления аккаунта."""
        handler = CancelAccountDeletionHandler(user_repo=user_repo)
        command = CancelAccountDeletionCommand(user_id=user_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Удаление аккаунта отменено"})

    async def disable_account(
        self,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Деактивация аккаунта."""
        handler = DisableAccountHandler(
            user_repo=user_repo,
            event_bus=event_bus,
        )
        command = DisableAccountCommand(user_id=user_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Аккаунт деактивирован"})

    async def reactivate_account(
        self,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Реактивация аккаунта."""
        handler = ReactivateAccountHandler(
            user_repo=user_repo,
            event_bus=event_bus,
        )
        command = ReactivateAccountCommand(user_id=user_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Аккаунт реактивирован"})

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def get_sessions(
        self,
        user_id: str = Depends(get_current_user_id),
        session_repo=Depends(get_session_repository),
    ) -> SuccessResponse[list[SessionResponse]]:
        """Активные сессии пользователя."""
        handler = GetActiveSessionsHandler(session_repo=session_repo)
        query = GetActiveSessionsQuery(user_id=user_id)
        dto = await handler.handle(query)
        sessions = [SessionResponse.model_validate(s.model_dump()) for s in dto.items]
        return SuccessResponse(data=sessions)

    async def terminate_session(
        self,
        session_id: str,
        user_id: str = Depends(get_current_user_id),
        session_repo=Depends(get_session_repository),
    ) -> MessageResponse:
        """Завершить одну сессию."""
        handler = TerminateSessionHandler(session_repo=session_repo)
        command = TerminateSessionCommand(user_id=user_id, session_id=session_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Сессия завершена"})

    async def terminate_all_sessions(
        self,
        body: TerminateAllSessionsRequest,
        user_id: str = Depends(get_current_user_id),
        session_repo=Depends(get_session_repository),
    ) -> SuccessResponse[TerminateAllSessionsResponse]:
        """Завершить все сессии кроме текущей."""
        handler = TerminateAllSessionsHandler(session_repo=session_repo)
        command = TerminateAllSessionsCommand(
            user_id=user_id,
            current_session_id=body.current_session_id,
        )
        count = await handler.handle(command)
        return SuccessResponse(data=TerminateAllSessionsResponse(terminated_count=count))

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------

    async def get_roles(
        self,
        name: str | None = Query(default=None, description="Фильтр по названию роли"),
        offset: int = Query(default=0, ge=0, description="Смещение для пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Лимит записей"),
        user_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_role_repository),
    ) -> SuccessResponse[list[RoleResponse]]:
        """Список ролей."""
        handler = GetRolesHandler(role_repo=role_repo)
        query = GetRolesQuery(name=name, offset=offset, limit=limit)
        dto = await handler.handle(query)
        roles = [RoleResponse.model_validate(r.model_dump()) for r in dto.items]
        return SuccessResponse(data=roles)

    async def get_role(
        self,
        role_id: str,
        user_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_role_repository),
    ) -> SuccessResponse[RoleResponse]:
        """Получить роль по ID."""
        handler = GetRoleByIdHandler(role_repo=role_repo)
        query = GetRoleByIdQuery(role_id=role_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=RoleResponse.model_validate(dto.model_dump()))
