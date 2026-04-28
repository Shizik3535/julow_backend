from __future__ import annotations

from fastapi import Depends, HTTPException, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.notification.application.commands.disable_dnd import (
    DisableDndCommand,
    DisableDndHandler,
)
from app.context.notification.application.commands.register_device_token import (
    RegisterDeviceTokenCommand,
    RegisterDeviceTokenHandler,
)
from app.context.notification.application.commands.remove_device_token import (
    RemoveDeviceTokenCommand,
    RemoveDeviceTokenHandler,
)
from app.context.notification.application.commands.set_notification_preference import (
    SetNotificationPreferenceCommand,
    SetNotificationPreferenceHandler,
)
from app.context.notification.application.commands.set_reminder_window import (
    SetReminderWindowCommand,
    SetReminderWindowHandler,
)
from app.context.notification.application.commands.update_digest_settings import (
    UpdateDigestSettingsCommand,
    UpdateDigestSettingsHandler,
)
from app.context.notification.application.commands.update_dnd_settings import (
    UpdateDndSettingsCommand,
    UpdateDndSettingsHandler,
)
from app.context.notification.application.queries.get_device_tokens import (
    GetDeviceTokensHandler,
    GetDeviceTokensQuery,
)
from app.context.notification.application.queries.get_digest_settings import (
    GetDigestSettingsHandler,
    GetDigestSettingsQuery,
)
from app.context.notification.application.queries.get_dnd_settings import (
    GetDndSettingsHandler,
    GetDndSettingsQuery,
)
from app.context.notification.application.queries.get_notification_preferences import (
    GetNotificationPreferencesHandler,
    GetNotificationPreferencesQuery,
)
from app.context.notification.application.queries.get_notification_types import (
    GetNotificationTypesHandler,
    GetNotificationTypesQuery,
)
from app.context.notification.presentation.dependencies import (
    get_current_user_id,
    get_device_token_repository,
    get_notification_event_bus,
    get_notification_preferences_repository,
)
from app.context.notification.presentation.schemas.requests.register_device_token_request import (
    RegisterDeviceTokenRequest,
)
from app.context.notification.presentation.schemas.requests.set_notification_preference_request import (
    SetNotificationPreferenceRequest,
)
from app.context.notification.presentation.schemas.requests.set_reminder_window_request import (
    SetReminderWindowRequest,
)
from app.context.notification.presentation.schemas.requests.update_digest_settings_request import (
    UpdateDigestSettingsRequest,
)
from app.context.notification.presentation.schemas.requests.update_dnd_settings_request import (
    UpdateDndSettingsRequest,
)
from app.context.notification.presentation.schemas.responses.device_token_response import (
    DeviceTokenResponse,
)
from app.context.notification.presentation.schemas.responses.digest_settings_response import (
    DigestSettingsResponse,
)
from app.context.notification.presentation.schemas.responses.dnd_settings_response import (
    DndSettingsResponse,
)
from app.context.notification.presentation.schemas.responses.notification_preferences_response import (
    NotificationPreferencesResponse,
)
from app.context.notification.presentation.schemas.responses.notification_type_response import (
    NotificationTypeResponse,
)


class NotificationSettingsController(BaseController):
    """
    Контроллер настроек уведомлений (Notification BC).

    Endpoint'ы:
        GET    /notification-settings/preferences           — Получить настройки
        POST   /notification-settings/preferences           — Установить настройку
        PUT    /notification-settings/reminder-window       — Установить окно напоминания
        GET    /notification-settings/types                — Получить типы уведомлений
        GET    /notification-settings/dnd                   — Получить настройки DND
        PUT    /notification-settings/dnd                   — Обновить DND
        POST   /notification-settings/dnd/disable           — Отключить DND
        GET    /notification-settings/digest                — Получить настройки дайджеста
        PUT    /notification-settings/digest                — Обновить дайджест
        GET    /notification-settings/devices               — Получить список устройств
        POST   /notification-settings/devices               — Зарегистрировать устройство
        DELETE /notification-settings/devices/{id}          — Удалить устройство
    """

    def __init__(self) -> None:
        super().__init__(prefix="/notification-settings", tags=["Notification Settings"])

    def _register_routes(self) -> None:
        # Preferences
        self._router.add_api_route(
            "/preferences",
            self.get_preferences,
            methods=["GET"],
            response_model=SuccessResponse[NotificationPreferencesResponse],
            summary="Получить настройки уведомлений",
            description="Возвращает глобальные настройки и переопределения по проектам.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/preferences",
            self.set_preference,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Установить настройку уведомлений",
            description="Устанавливает включение/отключение канала для типа уведомления.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # Reminder window
        self._router.add_api_route(
            "/reminder-window",
            self.set_reminder_window,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Установить окно напоминания",
            description="Устанавливает за сколько часов до дедлайна отправлять напоминание (1–168).",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # Notification types
        self._router.add_api_route(
            "/types",
            self.get_notification_types,
            methods=["GET"],
            response_model=SuccessResponse[list[NotificationTypeResponse]],
            summary="Получить типы уведомлений",
            description="Возвращает список всех типов уведомлений с описаниями и каналами по умолчанию.",
            responses={
                200: {"description": "Успех"},
            },
        )

        # DND
        self._router.add_api_route(
            "/dnd",
            self.get_dnd_settings,
            methods=["GET"],
            response_model=SuccessResponse[DndSettingsResponse],
            summary="Получить настройки DND",
            description="Возвращает текущие настройки режима «Не беспокоить».",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/dnd",
            self.update_dnd_settings,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки DND",
            description="Обновляет расписание режима «Не беспокоить».",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/dnd/disable",
            self.disable_dnd,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отключить DND",
            description="Отключает режим «Не беспокоить».",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
            },
        )

        # Digest
        self._router.add_api_route(
            "/digest",
            self.get_digest_settings,
            methods=["GET"],
            response_model=SuccessResponse[DigestSettingsResponse],
            summary="Получить настройки дайджеста",
            description="Возвращает текущие настройки дайджеста уведомлений.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/digest",
            self.update_digest_settings,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки дайджеста",
            description="Обновляет конфигурацию дайджеста уведомлений.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Настройки не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # Device tokens
        self._router.add_api_route(
            "/devices",
            self.get_device_tokens,
            methods=["GET"],
            response_model=SuccessResponse[list[DeviceTokenResponse]],
            summary="Получить список устройств",
            description="Возвращает список зарегистрированных push-токенов.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/devices",
            self.register_device_token,
            methods=["POST"],
            response_model=SuccessResponse[DeviceTokenResponse],
            status_code=201,
            summary="Зарегистрировать устройство",
            description="Регистрирует push-токен устройства для отправки push-уведомлений.",
            responses={
                201: {"description": "Устройство зарегистрировано"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/devices/{device_token_id}",
            self.remove_device_token,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить устройство",
            description="Деактивирует push-токен устройства.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Токен не найден", "model": ErrorResponse},
            },
        )

    # --- Preferences ---

    async def get_preferences(
        self,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
    ) -> SuccessResponse[NotificationPreferencesResponse]:
        """Получить настройки уведомлений."""
        handler = GetNotificationPreferencesHandler(preferences_repo=preferences_repo)
        query = GetNotificationPreferencesQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=NotificationPreferencesResponse.model_validate(dto.model_dump()))

    async def set_preference(
        self,
        body: SetNotificationPreferenceRequest,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Установить настройку уведомлений."""
        handler = SetNotificationPreferenceHandler(preferences_repo=preferences_repo, event_bus=event_bus)
        command = SetNotificationPreferenceCommand(
            user_id=user_id,
            notification_type=body.notification_type,
            channel=body.channel,
            enabled=body.enabled,
            scope=body.scope,
            scope_id=body.scope_id,
        )
        await handler.handle(command)
        return MessageResponse(data={"message": "Настройка обновлена"})

    # --- Reminder Window ---

    async def set_reminder_window(
        self,
        body: SetReminderWindowRequest,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Установить окно напоминания о дедлайне."""
        handler = SetReminderWindowHandler(preferences_repo=preferences_repo, event_bus=event_bus)
        command = SetReminderWindowCommand(user_id=user_id, hours=body.hours)
        await handler.handle(command)
        return MessageResponse(data={"message": "Окно напоминания обновлено"})

    # --- Notification Types ---

    async def get_notification_types(
        self,
    ) -> SuccessResponse[list[NotificationTypeResponse]]:
        """Получить список типов уведомлений."""
        handler = GetNotificationTypesHandler()
        query = GetNotificationTypesQuery()
        dto = await handler.handle(query)
        items = [NotificationTypeResponse.model_validate(t.model_dump()) for t in dto.items]
        return SuccessResponse(data=items)

    # --- DND ---

    async def get_dnd_settings(
        self,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
    ) -> SuccessResponse[DndSettingsResponse]:
        """Получить настройки DND."""
        handler = GetDndSettingsHandler(preferences_repo=preferences_repo)
        query = GetDndSettingsQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=DndSettingsResponse.model_validate(dto.model_dump()))

    async def update_dnd_settings(
        self,
        body: UpdateDndSettingsRequest,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Обновить настройки DND."""
        handler = UpdateDndSettingsHandler(preferences_repo=preferences_repo, event_bus=event_bus)
        command = UpdateDndSettingsCommand(
            user_id=user_id,
            enabled=body.enabled,
            schedule_start=body.schedule_start,
            schedule_end=body.schedule_end,
            schedule_days=body.schedule_days,
            timezone=body.timezone,
        )
        await handler.handle(command)
        return MessageResponse(data={"message": "Настройки DND обновлены"})

    async def disable_dnd(
        self,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Отключить DND."""
        handler = DisableDndHandler(preferences_repo=preferences_repo, event_bus=event_bus)
        command = DisableDndCommand(user_id=user_id)
        await handler.handle(command)
        return MessageResponse(data={"message": "Режим DND отключён"})

    # --- Digest ---

    async def get_digest_settings(
        self,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
    ) -> SuccessResponse[DigestSettingsResponse]:
        """Получить настройки дайджеста."""
        handler = GetDigestSettingsHandler(preferences_repo=preferences_repo)
        query = GetDigestSettingsQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=DigestSettingsResponse.model_validate(dto.model_dump()))

    async def update_digest_settings(
        self,
        body: UpdateDigestSettingsRequest,
        user_id: str = Depends(get_current_user_id),
        preferences_repo=Depends(get_notification_preferences_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Обновить настройки дайджеста."""
        handler = UpdateDigestSettingsHandler(preferences_repo=preferences_repo, event_bus=event_bus)
        command = UpdateDigestSettingsCommand(
            user_id=user_id,
            enabled=body.enabled,
            frequency=body.frequency,
            delivery_time=body.delivery_time,
            delivery_day=body.delivery_day,
            timezone=body.timezone,
        )
        await handler.handle(command)
        return MessageResponse(data={"message": "Настройки дайджеста обновлены"})

    # --- Device Tokens ---

    async def get_device_tokens(
        self,
        active_only: bool = Query(default=False, description="Только активные токены"),
        user_id: str = Depends(get_current_user_id),
        device_token_repo=Depends(get_device_token_repository),
    ) -> SuccessResponse[list[DeviceTokenResponse]]:
        """Получить список устройств."""
        handler = GetDeviceTokensHandler(device_token_repo=device_token_repo)
        query = GetDeviceTokensQuery(user_id=user_id, active_only=active_only)
        dto = await handler.handle(query)
        items = [DeviceTokenResponse.model_validate(t.model_dump()) for t in dto.items]
        return SuccessResponse(data=items)

    async def register_device_token(
        self,
        body: RegisterDeviceTokenRequest,
        user_id: str = Depends(get_current_user_id),
        device_token_repo=Depends(get_device_token_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> SuccessResponse[DeviceTokenResponse]:
        """Зарегистрировать устройство."""
        handler = RegisterDeviceTokenHandler(device_token_repo=device_token_repo, event_bus=event_bus)
        command = RegisterDeviceTokenCommand(
            user_id=user_id,
            token=body.token,
            platform=body.platform,
            device_name=body.device_name,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DeviceTokenResponse.model_validate(dto.model_dump()))

    async def remove_device_token(
        self,
        device_token_id: str,
        user_id: str = Depends(get_current_user_id),
        device_token_repo=Depends(get_device_token_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Удалить устройство."""
        from app.shared.domain.value_objects.id_vo import Id
        from app.context.notification.domain.exceptions.notification_exceptions import DeviceTokenNotFoundException

        device_token = await device_token_repo.get_by_id(Id.from_string(device_token_id))
        if device_token is None:
            raise DeviceTokenNotFoundException(device_token_id)
        if str(device_token.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому устройству")

        handler = RemoveDeviceTokenHandler(device_token_repo=device_token_repo, event_bus=event_bus)
        command = RemoveDeviceTokenCommand(device_token_id=device_token_id)
        await handler.handle(command)
        return MessageResponse(data={"message": "Устройство удалено"})
