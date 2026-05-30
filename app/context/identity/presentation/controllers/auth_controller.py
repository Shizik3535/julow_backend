from __future__ import annotations

from fastapi import Depends, Path, Query, Request

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.identity.application.commands.confirm_email import (
    ConfirmEmailCommand,
    ConfirmEmailHandler,
)
from app.context.identity.application.commands.initiate_sso_login import (
    InitiateSSOLoginCommand,
    InitiateSSOLoginHandler,
)
from app.context.identity.application.commands.login_oauth import (
    LoginOAuthCommand,
    LoginOAuthHandler,
)
from app.context.identity.application.commands.login_sso_callback import (
    LoginSSOCallbackCommand,
    LoginSSOCallbackHandler,
)
from app.context.identity.application.commands.login_user import (
    LoginUserCommand,
    LoginUserHandler,
)
from app.context.identity.application.commands.qr_login import (
    ConfirmQrLoginCommand,
    ConfirmQrLoginHandler,
    CreateQrLoginCommand,
    CreateQrLoginHandler,
    PollQrLoginHandler,
    PollQrLoginQuery,
)
from app.context.identity.application.commands.refresh_session import (
    RefreshSessionCommand,
    RefreshSessionHandler,
)
from app.context.identity.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from app.context.identity.application.commands.request_password_reset import (
    RequestPasswordResetCommand,
    RequestPasswordResetHandler,
)
from app.context.identity.application.commands.reset_password import (
    ResetPasswordCommand,
    ResetPasswordHandler,
)
from app.context.identity.presentation.dependencies import (
    get_auth_token_port,
    get_cache_port,
    get_current_user_id,
    get_failed_login_policy,
    get_identity_event_bus,
    get_identity_notification_port,
    get_oauth_port,
    get_organization_sso_port,
    get_password_port,
    get_role_repository,
    get_session_repository,
    get_sso_port,
    get_user_auth_repository,
    get_user_repository,
)
from app.context.identity.presentation.schemas.requests.confirm_qr_login_request import (
    ConfirmQrLoginRequest,
)
from app.context.identity.presentation.schemas.requests.create_qr_login_request import (
    CreateQrLoginRequest,
)
from app.context.identity.presentation.schemas.requests.refresh_session_request import (
    RefreshSessionRequest,
)
from app.context.identity.presentation.schemas.requests.confirm_email_request import (
    ConfirmEmailRequest,
)
from app.context.identity.presentation.schemas.requests.login_oauth_request import LoginOAuthRequest
from app.context.identity.presentation.schemas.requests.login_request import LoginRequest
from app.context.identity.presentation.schemas.requests.login_sso_callback_request import LoginSSOCallbackRequest
from app.context.identity.presentation.schemas.requests.login_sso_request import LoginSSORequest
from app.context.identity.presentation.schemas.requests.password_reset_confirm_request import (
    PasswordResetConfirmRequest,
)
from app.context.identity.presentation.schemas.requests.password_reset_request import (
    RequestPasswordResetRequest,
)
from app.context.identity.presentation.schemas.requests.register_request import RegisterRequest
from app.context.identity.presentation.schemas.responses.login_response import LoginResponse
from app.context.identity.presentation.schemas.responses.qr_login_responses import (
    QrLoginCreatedResponse,
    QrLoginPollResponse,
)
from app.context.identity.presentation.schemas.responses.oauth_authorize_response import OAuthAuthorizeResponse
from app.context.identity.presentation.schemas.responses.sso_authorize_response import SSOAuthorizeResponse
from app.context.identity.presentation.schemas.responses.user_response import UserResponse


class AuthController(BaseController):
    """
    Контроллер аутентификации Identity BC.

    Endpoint'ы:
        GET  /auth/oauth/{provider}/authorize  — URL авторизации OAuth-провайдера
        POST /auth/register                    — Регистрация нового пользователя
        POST /auth/login                       — Вход в систему
        POST /auth/login/oauth                 — Вход через OAuth-провайдер
        POST /auth/login/sso                   — Инициация SSO-логина
        POST /auth/login/sso/callback          — Callback от SSO IdP
        POST /auth/refresh                     — Обновление пары токенов
        POST /auth/confirm-email               — Подтверждение email-адреса
        POST /auth/password-reset/request      — Запрос сброса пароля
        POST /auth/password-reset/confirm      — Подтверждение сброса пароля
        POST /auth/qr/create                   — Создать QR-сессию (веб)
        POST /auth/qr/confirm                  — Подтвердить вход с телефона
        GET  /auth/qr/poll/{qr_token}          — Опрос статуса QR (веб)
    """

    def __init__(self) -> None:
        super().__init__(prefix="/auth", tags=["Identity / Auth"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/oauth/{provider}/authorize",
            self.oauth_authorize,
            methods=["GET"],
            response_model=SuccessResponse[OAuthAuthorizeResponse],
            summary="URL авторизации OAuth-провайдера",
            description=(
                "Возвращает URL для редиректа пользователя на страницу авторизации OAuth-провайдера. "
                "Фронтенд редиректит пользователя на этот URL, после авторизации "
                "провайдер возвращает authorization code, который отправляется на POST /auth/login/oauth."
            ),
            responses={
                200: {"description": "URL авторизации"},
                400: {"description": "Неизвестный OAuth-провайдер", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/register",
            self.register,
            methods=["POST"],
            response_model=SuccessResponse[UserResponse],
            status_code=201,
            summary="Регистрация пользователя",
            description=(
                "Создаёт нового пользователя с указанным email и паролем. "
                "Назначает роль по умолчанию (user). "
                "После регистрации статус аккаунта — `pending_verification`. "
                "Для активации необходимо подтвердить email."
            ),
            responses={
                201: {"description": "Пользователь успешно создан"},
                409: {"description": "Пользователь с таким email уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации входных данных", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=SuccessResponse[LoginResponse],
            summary="Вход в систему",
            description=(
                "Аутентифицирует пользователя по email и паролю. "
                "Возвращает JWT access/refresh токены и данные пользователя. "
                "При включённом флаге `is_remember_me` время жизни сессии увеличивается до 30 дней. "
                "IP-адрес и User-Agent извлекаются из запроса автоматически."
            ),
            responses={
                200: {"description": "Успешная аутентификация"},
                401: {"description": "Неверные учётные данные", "model": ErrorResponse},
                403: {"description": "Аккаунт заблокирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/login/oauth",
            self.login_oauth,
            methods=["POST"],
            response_model=SuccessResponse[LoginResponse],
            summary="Вход через OAuth-провайдер",
            description=(
                "Аутентифицирует пользователя через OAuth-провайдер. "
                "Обменивает authorization code на access token, получает профиль пользователя. "
                "Если пользователь уже привязан — выполняет вход. "
                "Если email совпадает с существующим аккаунтом — привязывает OAuth и выполняет вход. "
                "Если новый пользователь — автоматически регистрирует и выполняет вход. "
                "IP-адрес и User-Agent извлекаются из запроса автоматически."
            ),
            responses={
                200: {"description": "Успешная аутентификация"},
                401: {"description": "Невалидный authorization code", "model": ErrorResponse},
                403: {"description": "Аккаунт заблокирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/login/sso",
            self.login_sso,
            methods=["POST"],
            response_model=SuccessResponse[SSOAuthorizeResponse],
            summary="Инициация SSO-логина",
            description=(
                "Определяет SSO-провайдера по email-домену и возвращает URL для редиректа на IdP. "
                "Фронтенд редиректит пользователя на этот URL для аутентификации. "
                "После аутентификации IdP вызывает POST /auth/login/sso/callback."
            ),
            responses={
                200: {"description": "URL для редиректа на IdP"},
                401: {"description": "SSO не настроен для данного email-домена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/login/sso/callback",
            self.login_sso_callback,
            methods=["POST"],
            response_model=SuccessResponse[LoginResponse],
            summary="Callback от SSO IdP",
            description=(
                "Обрабатывает ответ от SSO IdP. "
                "Если пользователь уже привязан — выполняет вход. "
                "Если новый пользователь и auto_provision включён — авто-регистрация и вход."
            ),
            responses={
                200: {"description": "Успешная аутентификация"},
                401: {"description": "Ошибка SSO-аутентификации", "model": ErrorResponse},
                403: {"description": "Аккаунт заблокирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/refresh",
            self.refresh_session,
            methods=["POST"],
            response_model=SuccessResponse[LoginResponse],
            summary="Обновление пары токенов",
            description=(
                "Обновляет access/refresh токены по текущему refresh-токену. "
                "Старый refresh-токен становится недействительным. "
                "Возвращает новую пару токенов и данные пользователя."
            ),
            responses={
                200: {"description": "Токены обновлены"},
                401: {"description": "Невалидный или просроченный refresh-токен", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/confirm-email",
            self.confirm_email,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Подтверждение email",
            description=(
                "Подтверждает email-адрес пользователя по токену верификации. "
                "Токен отправляется на email при регистрации. "
                "После подтверждения статус аккаунта меняется на `active`."
            ),
            responses={
                200: {"description": "Email успешно подтверждён"},
                400: {"description": "Невалидный или просроченный токен", "model": ErrorResponse},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/password-reset/request",
            self.request_password_reset,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Запрос сброса пароля",
            description=(
                "Инициирует процесс сброса пароля. "
                "Генерирует токен сброса и отправляет его на указанный email. "
                "Всегда возвращает 200, даже если пользователь не найден "
                "(для предотвращения утечки информации о существовании аккаунта)."
            ),
            responses={
                200: {"description": "Запрос принят"},
            },
        )
        self._router.add_api_route(
            "/password-reset/confirm",
            self.reset_password,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Подтверждение сброса пароля",
            description=(
                "Выполняет смену пароля по ранее полученному токену сброса. "
                "Токен одноразовый — после использования становится недействительным."
            ),
            responses={
                200: {"description": "Пароль успешно изменён"},
                400: {"description": "Невалидный или просроченный токен", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/qr/create",
            self.create_qr_login,
            methods=["POST"],
            response_model=SuccessResponse[QrLoginCreatedResponse],
            summary="Создать QR-сессию для входа с веба",
            description=(
                "Генерирует одноразовый токен (TTL ~5 мин) для отображения в QR на странице входа. "
                "Мобильное приложение сканирует код и подтверждает через POST /auth/qr/confirm."
            ),
        )
        self._router.add_api_route(
            "/qr/confirm",
            self.confirm_qr_login,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Подтвердить QR-вход (мобильный клиент)",
            description=(
                "Требует Bearer access-токен авторизованного пользователя. "
                "Создаёт веб-сессию после подтверждения на телефоне."
            ),
            responses={
                200: {"description": "Подтверждено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "QR не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/qr/poll/{qr_token}",
            self.poll_qr_login,
            methods=["GET"],
            response_model=SuccessResponse[QrLoginPollResponse],
            summary="Опрос статуса QR-входа",
            description="Веб-клиент опрашивает до status=confirmed, затем получает токены один раз.",
        )

    async def oauth_authorize(
        self,
        provider: str = Path(..., description="Название OAuth-провайдера", examples=["oauth_google"]),
        redirect_uri: str | None = Query(None, description="URI перенаправления после авторизации"),
        state: str | None = Query(None, description="State-параметр для защиты от CSRF"),
        oauth_port=Depends(get_oauth_port),
    ) -> SuccessResponse[OAuthAuthorizeResponse]:
        """Получить URL авторизации OAuth-провайдера."""
        if redirect_uri is None:
            redirect_uri = ""
        authorize_url = oauth_port.get_authorize_url(
            provider=provider,
            redirect_uri=redirect_uri,
            state=state,
        )
        return SuccessResponse(
            data=OAuthAuthorizeResponse(provider=provider, authorize_url=authorize_url)
        )

    async def register(
        self,
        body: RegisterRequest,
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        role_repo=Depends(get_role_repository),
        password_port=Depends(get_password_port),
        event_bus=Depends(get_identity_event_bus),
        notification_port=Depends(get_identity_notification_port),
    ) -> SuccessResponse[UserResponse]:
        """Регистрация нового пользователя."""
        handler = RegisterUserHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            role_repo=role_repo,
            password_port=password_port,
            event_bus=event_bus,
            notification_port=notification_port,
        )
        command = RegisterUserCommand(
            email=body.email,
            password=body.password,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=UserResponse.model_validate(dto.model_dump()))

    async def login(
        self,
        body: LoginRequest,
        request: Request,
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        session_repo=Depends(get_session_repository),
        password_port=Depends(get_password_port),
        auth_token_port=Depends(get_auth_token_port),
        failed_login_policy=Depends(get_failed_login_policy),
        event_bus=Depends(get_identity_event_bus),
        org_sso_port=Depends(get_organization_sso_port),
    ) -> SuccessResponse[LoginResponse]:
        """Вход в систему."""
        handler = LoginUserHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            password_port=password_port,
            auth_token_port=auth_token_port,
            failed_login_policy=failed_login_policy,
            event_bus=event_bus,
            org_sso_port=org_sso_port,
        )
        command = LoginUserCommand(
            email=body.email,
            password=body.password,
            ip=request.client.host if request.client else "127.0.0.1",
            user_agent=request.headers.get("user-agent", "unknown"),
            is_remember_me=body.is_remember_me,
        )
        dto = await handler.handle(command)
        user_resp = UserResponse.model_validate(dto.user.model_dump())
        login_resp = LoginResponse(
            user=user_resp,
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            access_expires_in=dto.access_expires_in,
            refresh_expires_in=dto.refresh_expires_in,
        )
        return SuccessResponse(data=login_resp)

    async def login_oauth(
        self,
        body: LoginOAuthRequest,
        request: Request,
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        session_repo=Depends(get_session_repository),
        role_repo=Depends(get_role_repository),
        oauth_port=Depends(get_oauth_port),
        auth_token_port=Depends(get_auth_token_port),
        failed_login_policy=Depends(get_failed_login_policy),
        event_bus=Depends(get_identity_event_bus),
    ) -> SuccessResponse[LoginResponse]:
        """Вход через OAuth-провайдер."""
        handler = LoginOAuthHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            role_repo=role_repo,
            oauth_port=oauth_port,
            auth_token_port=auth_token_port,
            failed_login_policy=failed_login_policy,
            event_bus=event_bus,
        )
        command = LoginOAuthCommand(
            provider=body.provider,
            authorization_code=body.authorization_code,
            redirect_uri=body.redirect_uri,
            ip=request.client.host if request.client else "127.0.0.1",
            user_agent=request.headers.get("user-agent", "unknown"),
            is_remember_me=body.is_remember_me,
        )
        dto = await handler.handle(command)
        user_resp = UserResponse.model_validate(dto.user.model_dump())
        login_resp = LoginResponse(
            user=user_resp,
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            access_expires_in=dto.access_expires_in,
            refresh_expires_in=dto.refresh_expires_in,
        )
        return SuccessResponse(data=login_resp)

    async def login_sso(
        self,
        body: LoginSSORequest,
        request: Request,
        org_sso_port=Depends(get_organization_sso_port),
        sso_port=Depends(get_sso_port),
    ) -> SuccessResponse[SSOAuthorizeResponse]:
        """Инициация SSO-логина."""
        callback_url = str(request.url_for("login_sso_callback"))
        handler = InitiateSSOLoginHandler(
            org_sso_port=org_sso_port,
            sso_port=sso_port,
        )
        command = InitiateSSOLoginCommand(
            email=body.email,
            callback_url=callback_url,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=SSOAuthorizeResponse(redirect_url=dto.redirect_url))

    async def login_sso_callback(
        self,
        body: LoginSSOCallbackRequest,
        request: Request,
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        session_repo=Depends(get_session_repository),
        role_repo=Depends(get_role_repository),
        org_sso_port=Depends(get_organization_sso_port),
        sso_port=Depends(get_sso_port),
        auth_token_port=Depends(get_auth_token_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> SuccessResponse[LoginResponse]:
        """Callback от SSO IdP."""
        callback_url = str(request.url_for("login_sso_callback"))
        handler = LoginSSOCallbackHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            role_repo=role_repo,
            org_sso_port=org_sso_port,
            sso_port=sso_port,
            auth_token_port=auth_token_port,
            event_bus=event_bus,
        )
        command = LoginSSOCallbackCommand(
            email_domain=body.email_domain,
            response_data=body.response_data,
            callback_url=callback_url,
            ip=request.client.host if request.client else "127.0.0.1",
            user_agent=request.headers.get("user-agent", "unknown"),
        )
        dto = await handler.handle(command)
        user_resp = UserResponse.model_validate(dto.user.model_dump())
        login_resp = LoginResponse(
            user=user_resp,
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            access_expires_in=dto.access_expires_in,
            refresh_expires_in=dto.refresh_expires_in,
        )
        return SuccessResponse(data=login_resp)

    async def refresh_session(
        self,
        body: RefreshSessionRequest,
        session_repo=Depends(get_session_repository),
        user_repo=Depends(get_user_repository),
        auth_token_port=Depends(get_auth_token_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> SuccessResponse[LoginResponse]:
        """Обновление пары токенов по refresh-токену."""
        handler = RefreshSessionHandler(
            session_repo=session_repo,
            user_repo=user_repo,
            auth_token_port=auth_token_port,
            event_bus=event_bus,
        )
        command = RefreshSessionCommand(refresh_token=body.refresh_token)
        dto = await handler.handle(command)
        user_resp = UserResponse.model_validate(dto.user.model_dump())
        login_resp = LoginResponse(
            user=user_resp,
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            access_expires_in=dto.access_expires_in,
            refresh_expires_in=dto.refresh_expires_in,
        )
        return SuccessResponse(data=login_resp)

    async def confirm_email(
        self,
        body: ConfirmEmailRequest,
        user_id: str = Depends(get_current_user_id),
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Подтверждение email-адреса."""
        handler = ConfirmEmailHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )
        command = ConfirmEmailCommand(
            user_id=user_id,
            token=body.token,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Email успешно подтверждён"})

    async def request_password_reset(
        self,
        body: RequestPasswordResetRequest,
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
        notification_port=Depends(get_identity_notification_port),
    ) -> MessageResponse:
        """Запрос сброса пароля."""
        handler = RequestPasswordResetHandler(
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
            notification_port=notification_port,
        )
        command = RequestPasswordResetCommand(email=body.email)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Инструкции по сбросу пароля отправлены на email"})

    async def reset_password(
        self,
        body: PasswordResetConfirmRequest,
        user_auth_repo=Depends(get_user_auth_repository),
        password_port=Depends(get_password_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Подтверждение сброса пароля."""
        handler = ResetPasswordHandler(
            user_auth_repo=user_auth_repo,
            password_port=password_port,
            event_bus=event_bus,
        )
        command = ResetPasswordCommand(
            email=body.email,
            token=body.token,
            new_password=body.new_password,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Пароль успешно изменён"})

    async def create_qr_login(
        self,
        request: Request,
        body: CreateQrLoginRequest = CreateQrLoginRequest(),
        cache_port=Depends(get_cache_port),
    ) -> SuccessResponse[QrLoginCreatedResponse]:
        """Создать QR-токен для веб-входа."""
        handler = CreateQrLoginHandler(cache_port=cache_port)
        command = CreateQrLoginCommand(
            ip=request.client.host if request.client else "127.0.0.1",
            user_agent=request.headers.get("user-agent", "unknown"),
            web_origin=body.web_origin,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=QrLoginCreatedResponse.model_validate(dto.model_dump()))

    async def confirm_qr_login(
        self,
        body: ConfirmQrLoginRequest,
        request: Request,
        user_id: str = Depends(get_current_user_id),
        cache_port=Depends(get_cache_port),
        user_repo=Depends(get_user_repository),
        user_auth_repo=Depends(get_user_auth_repository),
        session_repo=Depends(get_session_repository),
        auth_token_port=Depends(get_auth_token_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Подтвердить QR-вход с мобильного устройства."""
        handler = ConfirmQrLoginHandler(
            cache_port=cache_port,
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            auth_token_port=auth_token_port,
            event_bus=event_bus,
        )
        command = ConfirmQrLoginCommand(
            qr_token=body.qr_token,
            approver_user_id=user_id,
            ip=request.client.host if request.client else "127.0.0.1",
            user_agent=request.headers.get("user-agent", "julow-mobile"),
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Вход на веб подтверждён"})

    async def poll_qr_login(
        self,
        qr_token: str = Path(..., description="Токен из QR"),
        cache_port=Depends(get_cache_port),
    ) -> SuccessResponse[QrLoginPollResponse]:
        """Опрос статуса QR-входа."""
        handler = PollQrLoginHandler(cache_port=cache_port)
        dto = await handler.handle(PollQrLoginQuery(qr_token=qr_token))
        return SuccessResponse(data=QrLoginPollResponse.model_validate(dto.model_dump()))
