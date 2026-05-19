from __future__ import annotations

from fastapi import Depends, HTTPException, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.notification.application.commands.archive_notification import (
    ArchiveNotificationCommand,
    ArchiveNotificationHandler,
)
from app.context.notification.application.commands.mark_all_notifications_read import (
    MarkAllNotificationsReadCommand,
    MarkAllNotificationsReadHandler,
)
from app.context.notification.application.commands.mark_notification_read import (
    MarkNotificationReadCommand,
    MarkNotificationReadHandler,
)
from app.context.notification.application.queries.get_notifications import (
    GetNotificationsHandler,
    GetNotificationsQuery,
)
from app.context.notification.application.queries.get_connection_info import (
    GetConnectionInfoHandler,
    GetConnectionInfoQuery,
)
from app.context.notification.application.queries.get_unread_count import (
    GetUnreadCountHandler,
    GetUnreadCountQuery,
)
from app.context.notification.presentation.dependencies import (
    get_current_user_id,
    get_notification_event_bus,
    get_notification_repository,
    get_settings,
)
from app.context.notification.presentation.schemas.responses.connection_info_response import (
    ConnectionInfoResponse,
)
from app.context.notification.presentation.schemas.responses.notification_response import (
    NotificationResponse,
)
from app.context.notification.presentation.schemas.responses.unread_count_response import (
    UnreadCountResponse,
)
from app.context.notification.presentation.schemas.requests.mark_all_read_request import (
    MarkAllReadRequest,
)


class NotificationController(BaseController):
    """
    Контроллер уведомлений (Notification BC).

    Endpoint'ы:
        GET    /notifications               — Получить список уведомлений
        GET    /notifications/connection-info — Информация о подключении WS
        GET    /notifications/unread-count  — Количество непрочитанных
        PATCH  /notifications/{id}/read     — Пометить как прочитанное
        POST   /notifications/read-all      — Пометить все как прочитанные
        PATCH  /notifications/{id}/archive  — Архивировать
    """

    def __init__(self) -> None:
        super().__init__(prefix="/notifications", tags=["Notifications"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/connection-info",
            self.get_connection_info,
            methods=["GET"],
            response_model=SuccessResponse[ConnectionInfoResponse],
            summary="Информация о подключении к real-time уведомлениям",
            description="Возвращает URL WebSocket, схему авторизации, типы событий и протокол взаимодействия.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/",
            self.get_notifications,
            methods=["GET"],
            response_model=SuccessResponse[list[NotificationResponse]],
            summary="Получить список уведомлений",
            description="Возвращает список уведомлений текущего пользователя с фильтрацией и пагинацией.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/unread-count",
            self.get_unread_count,
            methods=["GET"],
            response_model=SuccessResponse[UnreadCountResponse],
            summary="Количество непрочитанных уведомлений",
            description="Возвращает количество непрочитанных уведомлений, в т.ч. по workspace.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{notification_id}/read",
            self.mark_read,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Пометить уведомление как прочитанное",
            description="Помечает указанное уведомление как прочитанное.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Уведомление не найдено", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/read-all",
            self.mark_all_read,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Пометить все уведомления как прочитанные",
            description="Помечает все непрочитанные уведомления пользователя как прочитанные.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{notification_id}/archive",
            self.archive,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Архивировать уведомление",
            description="Перемещает уведомление в архив.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Уведомление не найдено", "model": ErrorResponse},
            },
        )

    async def get_connection_info(
        self,
        user_id: str = Depends(get_current_user_id),
        settings=Depends(get_settings),
    ) -> SuccessResponse[ConnectionInfoResponse]:
        """Получить информацию о подключении к real-time уведомлениям."""
        handler = GetConnectionInfoHandler(
            host=settings.app.host,
            port=settings.app.port,
            api_prefix=settings.app.api_prefix,
            debug=settings.app.debug,
            base_url=settings.app.base_url,
        )
        query = GetConnectionInfoQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ConnectionInfoResponse.model_validate(dto.model_dump()))

    async def get_notifications(
        self,
        workspace_id: str | None = Query(default=None, description="Фильтр по workspace UUID"),
        notification_type: str | None = Query(default=None, description="Фильтр по типу уведомления"),
        is_read: bool | None = Query(default=None, description="Фильтр по прочитанности"),
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        limit: int = Query(default=20, ge=1, le=100, description="Размер страницы"),
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_notification_repository),
    ) -> SuccessResponse[list[NotificationResponse]]:
        """Получить список уведомлений."""
        handler = GetNotificationsHandler(notification_repo=repo)
        query = GetNotificationsQuery(
            user_id=user_id,
            workspace_id=workspace_id,
            notification_type=notification_type,
            is_read=is_read,
            page=page,
            limit=limit,
        )
        dto = await handler.handle(query)
        items = [NotificationResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_unread_count(
        self,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_notification_repository),
    ) -> SuccessResponse[UnreadCountResponse]:
        """Получить количество непрочитанных уведомлений."""
        handler = GetUnreadCountHandler(notification_repo=repo)
        query = GetUnreadCountQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=UnreadCountResponse.model_validate(dto.model_dump()))

    async def mark_read(
        self,
        notification_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_notification_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Пометить уведомление как прочитанное."""
        from app.shared.domain.value_objects.id_vo import Id
        from app.context.notification.domain.exceptions.notification_exceptions import NotificationNotFoundException

        notification = await repo.get_by_id(Id.from_string(notification_id))
        if notification is None:
            raise NotificationNotFoundException(notification_id)
        if str(notification.recipient_id) != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому уведомлению")

        handler = MarkNotificationReadHandler(notification_repo=repo, event_bus=event_bus)
        command = MarkNotificationReadCommand(notification_id=notification_id)
        await handler.handle(command)
        return MessageResponse(data={"message": "Уведомление помечено как прочитанное"})

    async def mark_all_read(
        self,
        body: MarkAllReadRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_notification_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Пометить все уведомления как прочитанные."""
        handler = MarkAllNotificationsReadHandler(notification_repo=repo, event_bus=event_bus)
        command = MarkAllNotificationsReadCommand(user_id=user_id, workspace_id=body.workspace_id)
        count = await handler.handle(command)
        return MessageResponse(data={"message": f"Помечено прочитанными: {count}"})

    async def archive(
        self,
        notification_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_notification_repository),
        event_bus=Depends(get_notification_event_bus),
    ) -> MessageResponse:
        """Архивировать уведомление."""
        from app.shared.domain.value_objects.id_vo import Id
        from app.context.notification.domain.exceptions.notification_exceptions import NotificationNotFoundException

        notification = await repo.get_by_id(Id.from_string(notification_id))
        if notification is None:
            raise NotificationNotFoundException(notification_id)
        if str(notification.recipient_id) != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому уведомлению")

        handler = ArchiveNotificationHandler(notification_repo=repo, event_bus=event_bus)
        command = ArchiveNotificationCommand(notification_id=notification_id)
        await handler.handle(command)
        return MessageResponse(data={"message": "Уведомление архивировано"})
