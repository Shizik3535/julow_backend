from __future__ import annotations

from fastapi import Depends, Request

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.identity.application.commands.add_trusted_device import (
    AddTrustedDeviceCommand,
    AddTrustedDeviceHandler,
)
from app.context.identity.application.commands.disable_auth_factor import (
    DisableAuthFactorCommand,
    DisableAuthFactorHandler,
)
from app.context.identity.application.commands.enable_auth_factor import (
    EnableAuthFactorCommand,
    EnableAuthFactorHandler,
)
from app.context.identity.application.commands.generate_backup_codes import (
    GenerateBackupCodesCommand,
    GenerateBackupCodesHandler,
)
from app.context.identity.application.commands.link_oauth import (
    LinkOAuthCommand,
    LinkOAuthHandler,
)
from app.context.identity.application.commands.remove_trusted_device import (
    RemoveTrustedDeviceCommand,
    RemoveTrustedDeviceHandler,
)
from app.context.identity.application.commands.set_primary_auth_factor import (
    SetPrimaryAuthFactorCommand,
    SetPrimaryAuthFactorHandler,
)
from app.context.identity.application.commands.unlink_oauth import (
    UnlinkOAuthCommand,
    UnlinkOAuthHandler,
)
from app.context.identity.application.commands.use_backup_code import (
    UseBackupCodeCommand,
    UseBackupCodeHandler,
)
from app.context.identity.application.commands.verify_auth_factor import (
    VerifyAuthFactorCommand,
    VerifyAuthFactorHandler,
)
from app.context.identity.application.queries.get_oauth_links import (
    GetOAuthLinksHandler,
    GetOAuthLinksQuery,
)
from app.context.identity.application.queries.get_trusted_devices import (
    GetTrustedDevicesHandler,
    GetTrustedDevicesQuery,
)
from app.context.identity.application.queries.get_user_auth_status import (
    GetUserAuthStatusHandler,
    GetUserAuthStatusQuery,
)
from app.context.identity.presentation.dependencies import (
    get_current_user_id,
    get_identity_event_bus,
    get_oauth_port,
    get_password_port,
    get_totp_port,
    get_user_auth_repository,
)
from app.context.identity.presentation.schemas.requests.add_trusted_device_request import (
    AddTrustedDeviceRequest,
)
from app.context.identity.presentation.schemas.requests.disable_auth_factor_request import (
    DisableAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.enable_auth_factor_request import (
    EnableAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.generate_backup_codes_request import (
    GenerateBackupCodesRequest,
)
from app.context.identity.presentation.schemas.requests.link_oauth_request import LinkOAuthRequest
from app.context.identity.presentation.schemas.requests.set_primary_auth_factor_request import (
    SetPrimaryAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.use_backup_code_request import (
    UseBackupCodeRequest,
)
from app.context.identity.presentation.schemas.requests.verify_auth_factor_request import (
    VerifyAuthFactorRequest,
)
from app.context.identity.presentation.schemas.responses.backup_codes_response import (
    BackupCodesResponse,
)
from app.context.identity.presentation.schemas.responses.enable_auth_factor_result_response import (
    EnableAuthFactorResultResponse,
)
from app.context.identity.presentation.schemas.responses.oauth_link_response import (
    OAuthLinkResponse,
)
from app.context.identity.presentation.schemas.responses.trusted_device_response import (
    TrustedDeviceResponse,
)
from app.context.identity.presentation.schemas.responses.user_auth_status_response import (
    UserAuthStatusResponse,
)


class SecurityController(BaseController):
    """
    Контроллер безопасности Identity BC.

    Endpoint'ы:
        GET    /account/security/status                          — Обзор безопасности аккаунта
        POST   /account/security/2fa/enable                      — Включить фактор 2FA
        POST   /account/security/2fa/disable                     — Отключить фактор 2FA
        POST   /account/security/2fa/verify                      — Проверить код 2FA
        POST   /account/security/2fa/set-primary                 — Установить основной фактор 2FA
        POST   /account/security/2fa/backup-codes                — Сгенерировать резервные коды
        POST   /account/security/2fa/use-backup-code             — Использовать резервный код
        GET    /account/security/oauth                           — Список привязанных OAuth-провайдеров
        POST   /account/security/oauth/link                      — Привязать OAuth-провайдер
        DELETE /account/security/oauth/{provider}                — Отвязать OAuth-провайдер
        GET    /account/security/trusted-devices                 — Список доверенных устройств
        POST   /account/security/trusted-devices                 — Добавить доверенное устройство
        DELETE /account/security/trusted-devices/{fingerprint}   — Удалить доверенное устройство
    """

    def __init__(self) -> None:
        super().__init__(prefix="/account/security", tags=["Identity / Security"])

    def _register_routes(self) -> None:
        # --- Status ---
        self._router.add_api_route(
            "/status",
            self.get_auth_status,
            methods=["GET"],
            response_model=SuccessResponse[UserAuthStatusResponse],
            summary="Обзор безопасности аккаунта",
            description=(
                "Возвращает сводку по безопасности аккаунта: наличие пароля, "
                "статус блокировки, факторы 2FA, количество OAuth-провайдеров, "
                "доверенных устройств и оставшихся резервных кодов."
            ),
            responses={
                200: {"description": "Обзор безопасности"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )

        # --- 2FA ---
        self._router.add_api_route(
            "/2fa/enable",
            self.enable_auth_factor,
            methods=["POST"],
            response_model=SuccessResponse[EnableAuthFactorResultResponse],
            summary="Включить фактор 2FA",
            description=(
                "Включает указанный фактор двухфакторной аутентификации. "
                "Поддерживаемые методы: totp, email_code, app. "
                "Для TOTP сервер генерирует секрет и возвращает provisioning URI для QR-кода. "
                "Параметр `is_primary` позволяет назначить фактор основным."
            ),
            responses={
                200: {"description": "Фактор 2FA включён, возвращен provisioning URI"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/2fa/disable",
            self.disable_auth_factor,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отключить фактор 2FA",
            description=(
                "Отключает указанный фактор двухфакторной аутентификации. "
                "Нельзя отключить последний активный фактор."
            ),
            responses={
                200: {"description": "Фактор 2FA отключён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/2fa/verify",
            self.verify_auth_factor,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Проверить код 2FA",
            description=(
                "Проверяет одноразовый код двухфакторной аутентификации. "
                "При неверном коде возвращает ошибку 400."
            ),
            responses={
                200: {"description": "Код верифицирован"},
                400: {"description": "Неверный код 2FA", "model": ErrorResponse},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/2fa/set-primary",
            self.set_primary_auth_factor,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Установить основной фактор 2FA",
            description=(
                "Назначает указанный метод 2FA основным фактором аутентификации. "
                "Фактор должен быть включён."
            ),
            responses={
                200: {"description": "Основной фактор установлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/2fa/backup-codes",
            self.generate_backup_codes,
            methods=["POST"],
            response_model=SuccessResponse[BackupCodesResponse],
            summary="Сгенерировать резервные коды",
            description=(
                "Генерирует новые резервные коды 2FA. Старые коды заменяются. "
                "Коды показываются один раз — сохраните их в безопасном месте."
            ),
            responses={
                200: {"description": "Резервные коды сгенерированы"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/2fa/use-backup-code",
            self.use_backup_code,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Использовать резервный код",
            description=(
                "Верифицирует и использует резервный код 2FA. "
                "Каждый код одноразовый — после использования становится недействительным."
            ),
            responses={
                200: {"description": "Резервный код использован"},
                400: {"description": "Неверный резервный код", "model": ErrorResponse},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )

        # --- OAuth ---
        self._router.add_api_route(
            "/oauth",
            self.get_oauth_links,
            methods=["GET"],
            response_model=SuccessResponse[list[OAuthLinkResponse]],
            summary="Список привязанных OAuth-провайдеров",
            description=(
                "Возвращает список всех OAuth-провайдеров, привязанных к аккаунту. "
                "Включает название провайдера, email и время привязки."
            ),
            responses={
                200: {"description": "Список OAuth-провайдеров"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/oauth/link",
            self.link_oauth,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Привязать OAuth-провайдер",
            description=(
                "Привязывает внешний OAuth-провайдер к аккаунту. "
                "Поддерживаемые провайдеры: oauth_google, oauth_github, oauth_yandex, oauth_apple."
            ),
            responses={
                200: {"description": "OAuth-провайдер привязан"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Провайдер уже привязан", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/oauth/{provider}",
            self.unlink_oauth,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Отвязать OAuth-провайдер",
            description=(
                "Отвязывает указанный OAuth-провайдер от аккаунта. "
                "Нельзя отвязать последний метод входа."
            ),
            responses={
                200: {"description": "OAuth-провайдер отвязан"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
                409: {"description": "Нельзя отвязать последний метод входа", "model": ErrorResponse},
            },
        )

        # --- Trusted Devices ---
        self._router.add_api_route(
            "/trusted-devices",
            self.get_trusted_devices,
            methods=["GET"],
            response_model=SuccessResponse[list[TrustedDeviceResponse]],
            summary="Список доверенных устройств",
            description=(
                "Возвращает список доверенных устройств текущего пользователя. "
                "Просроченные устройства не включаются в результат."
            ),
            responses={
                200: {"description": "Список доверенных устройств"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/trusted-devices",
            self.add_trusted_device,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить доверенное устройство",
            description=(
                "Добавляет текущее устройство в список доверенных. "
                "IP-адрес и User-Agent извлекаются из запроса автоматически."
            ),
            responses={
                200: {"description": "Устройство добавлено в доверенные"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/trusted-devices/{fingerprint}",
            self.remove_trusted_device,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить доверенное устройство",
            description="Удаляет указанное устройство из списка доверенных.",
            responses={
                200: {"description": "Устройство удалено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Пользователь не найден", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_auth_status(
        self,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
    ) -> SuccessResponse[UserAuthStatusResponse]:
        """Обзор безопасности аккаунта."""
        handler = GetUserAuthStatusHandler(user_auth_repo=user_auth_repo)
        query = GetUserAuthStatusQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=UserAuthStatusResponse.model_validate(dto.model_dump()))

    # ------------------------------------------------------------------
    # 2FA
    # ------------------------------------------------------------------

    async def enable_auth_factor(
        self,
        body: EnableAuthFactorRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        totp_port=Depends(get_totp_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> SuccessResponse[EnableAuthFactorResultResponse]:
        """Включить фактор 2FA."""
        handler = EnableAuthFactorHandler(
            user_auth_repo=user_auth_repo,
            totp_port=totp_port,
            event_bus=event_bus,
        )
        command = EnableAuthFactorCommand(
            user_id=user_id,
            method=body.method,
            is_primary=body.is_primary,
        )
        dto = await handler.handle(command)
        return SuccessResponse(
            data=EnableAuthFactorResultResponse.model_validate(dto.model_dump()),
        )

    async def disable_auth_factor(
        self,
        body: DisableAuthFactorRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Отключить фактор 2FA."""
        handler = DisableAuthFactorHandler(
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )
        command = DisableAuthFactorCommand(
            user_id=user_id,
            method=body.method,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Фактор 2FA отключён"})

    async def verify_auth_factor(
        self,
        body: VerifyAuthFactorRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        totp_port=Depends(get_totp_port),
    ) -> MessageResponse:
        """Проверить код 2FA."""
        handler = VerifyAuthFactorHandler(
            user_auth_repo=user_auth_repo,
            totp_port=totp_port,
        )
        command = VerifyAuthFactorCommand(
            user_id=user_id,
            method=body.method,
            code=body.code,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Код 2FA верифицирован"})

    async def set_primary_auth_factor(
        self,
        body: SetPrimaryAuthFactorRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
    ) -> MessageResponse:
        """Установить основной фактор 2FA."""
        handler = SetPrimaryAuthFactorHandler(
            user_auth_repo=user_auth_repo,
        )
        command = SetPrimaryAuthFactorCommand(
            user_id=user_id,
            method=body.method,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Основной фактор 2FA установлен"})

    async def generate_backup_codes(
        self,
        body: GenerateBackupCodesRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        password_port=Depends(get_password_port),
    ) -> SuccessResponse[BackupCodesResponse]:
        """Сгенерировать резервные коды."""
        handler = GenerateBackupCodesHandler(
            user_auth_repo=user_auth_repo,
            password_port=password_port,
        )
        command = GenerateBackupCodesCommand(
            user_id=user_id,
            count=body.count,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=BackupCodesResponse.model_validate(dto.model_dump()))

    async def use_backup_code(
        self,
        body: UseBackupCodeRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        password_port=Depends(get_password_port),
    ) -> MessageResponse:
        """Использовать резервный код."""
        handler = UseBackupCodeHandler(
            user_auth_repo=user_auth_repo,
            password_port=password_port,
        )
        command = UseBackupCodeCommand(
            user_id=user_id,
            code=body.code,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Резервный код использован"})

    # ------------------------------------------------------------------
    # OAuth
    # ------------------------------------------------------------------

    async def get_oauth_links(
        self,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
    ) -> SuccessResponse[list[OAuthLinkResponse]]:
        """Список привязанных OAuth-провайдеров."""
        handler = GetOAuthLinksHandler(user_auth_repo=user_auth_repo)
        query = GetOAuthLinksQuery(user_id=user_id)
        dto = await handler.handle(query)
        links = [OAuthLinkResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=links)

    async def link_oauth(
        self,
        body: LinkOAuthRequest,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        oauth_port=Depends(get_oauth_port),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Привязать OAuth-провайдер."""
        handler = LinkOAuthHandler(
            user_auth_repo=user_auth_repo,
            oauth_port=oauth_port,
            event_bus=event_bus,
        )
        command = LinkOAuthCommand(
            user_id=user_id,
            provider=body.provider,
            authorization_code=body.authorization_code,
            redirect_uri=body.redirect_uri,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "OAuth-провайдер привязан"})

    async def unlink_oauth(
        self,
        provider: str,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Отвязать OAuth-провайдер."""
        handler = UnlinkOAuthHandler(
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )
        command = UnlinkOAuthCommand(
            user_id=user_id,
            provider=provider,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "OAuth-провайдер отвязан"})

    # ------------------------------------------------------------------
    # Trusted Devices
    # ------------------------------------------------------------------

    async def get_trusted_devices(
        self,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
    ) -> SuccessResponse[list[TrustedDeviceResponse]]:
        """Список доверенных устройств."""
        handler = GetTrustedDevicesHandler(user_auth_repo=user_auth_repo)
        query = GetTrustedDevicesQuery(user_id=user_id)
        dto = await handler.handle(query)
        devices = [TrustedDeviceResponse.model_validate(d.model_dump()) for d in dto.items]
        return SuccessResponse(data=devices)

    async def add_trusted_device(
        self,
        body: AddTrustedDeviceRequest,
        request: Request,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Добавить доверенное устройство."""
        handler = AddTrustedDeviceHandler(
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )
        command = AddTrustedDeviceCommand(
            user_id=user_id,
            device_fingerprint=body.device_fingerprint,
            user_agent=request.headers.get("user-agent", "unknown"),
            ip=request.client.host if request.client else "127.0.0.1",
            expires_at=body.expires_at,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Устройство добавлено в доверенные"})

    async def remove_trusted_device(
        self,
        fingerprint: str,
        user_id: str = Depends(get_current_user_id),
        user_auth_repo=Depends(get_user_auth_repository),
        event_bus=Depends(get_identity_event_bus),
    ) -> MessageResponse:
        """Удалить доверенное устройство."""
        handler = RemoveTrustedDeviceHandler(
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )
        command = RemoveTrustedDeviceCommand(
            user_id=user_id,
            device_fingerprint=fingerprint,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Доверенное устройство удалено"})
