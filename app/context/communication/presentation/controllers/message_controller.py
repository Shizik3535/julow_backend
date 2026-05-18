from __future__ import annotations

from fastapi import Depends, File, Form, Query, UploadFile

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse as HttpMessageResponse,
    SuccessResponse,
)

from app.context.communication.application.commands.delete_message import (
    DeleteMessageCommand,
    DeleteMessageHandler,
)
from app.context.communication.application.commands.manage_message_attachment import (
    AddMessageAttachmentCommand,
    AddMessageAttachmentHandler,
    RemoveMessageAttachmentCommand,
    RemoveMessageAttachmentHandler,
)
from app.context.communication.application.commands.manage_message_reaction import (
    AddMessageReactionCommand,
    AddMessageReactionHandler,
    RemoveMessageReactionCommand,
    RemoveMessageReactionHandler,
)
from app.context.communication.application.commands.send_message import (
    SendMessageCommand,
    SendMessageHandler,
)
from app.context.communication.application.commands.update_message import (
    UpdateMessageCommand,
    UpdateMessageHandler,
)
from app.context.communication.application.queries.get_messages_by_chat import (
    GetMessagesByChatHandler,
    GetMessagesByChatQuery,
)
from app.context.communication.application.queries.get_thread_messages import (
    GetThreadMessagesHandler,
    GetThreadMessagesQuery,
)
from app.context.communication.presentation.dependencies import (
    get_chat_repository,
    get_communication_event_bus,
    get_communication_file_attachment_port,
    get_current_user_id,
    get_message_repository,
)
from app.context.filestorage.presentation.dependencies import get_file_repository
from app.context.communication.presentation.schemas.requests.message_requests import (
    AddMessageReactionRequest,
    SendMessageRequest,
    UpdateMessageRequest,
)
from app.context.communication.presentation.schemas.responses.attachment_response import (
    AttachmentResponse,
)
from app.context.communication.presentation.schemas.responses.message_response import (
    MessageListResponse,
    MessageResponse,
)


class MessageController(BaseController):
    """
    Контроллер сообщений чата (Communication BC).

    Endpoint'ы (REST):
        POST   /chats/{chat_id}/messages                          — отправить сообщение
        GET    /chats/{chat_id}/messages                          — список с пагинацией
        GET    /chats/{chat_id}/threads/{thread_id}/messages      — сообщения треда
        PATCH  /messages/{message_id}                             — редактировать (автор)
        DELETE /messages/{message_id}                             — soft-delete (автор/admin)
        POST   /messages/{message_id}/reactions                   — добавить реакцию
        DELETE /messages/{message_id}/reactions/{emoji}           — снять реакцию
        POST   /messages/{message_id}/attachments                 — добавить вложение
        DELETE /messages/{message_id}/attachments/{attachment_id} — удалить вложение
    """

    def __init__(self) -> None:
        # Без префикса — пути миксованные (chat-scoped + message-scoped)
        super().__init__(prefix="", tags=["Messages"])

    def _register_routes(self) -> None:
        unauth = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse}
        }

        self._router.add_api_route(
            "/chats/{chat_id}/messages",
            self.send_message,
            methods=["POST"],
            response_model=SuccessResponse[MessageResponse],
            status_code=201,
            summary="Отправить сообщение в чат",
            responses=unauth,
        )
        self._router.add_api_route(
            "/chats/{chat_id}/messages",
            self.list_messages,
            methods=["GET"],
            response_model=SuccessResponse[MessageListResponse],
            summary="Список сообщений чата с пагинацией",
            responses=unauth,
        )
        self._router.add_api_route(
            "/chats/{chat_id}/threads/{thread_id}/messages",
            self.list_thread_messages,
            methods=["GET"],
            response_model=SuccessResponse[MessageListResponse],
            summary="Сообщения треда",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}",
            self.update_message,
            methods=["PATCH"],
            response_model=SuccessResponse[MessageResponse],
            summary="Редактировать сообщение (автор)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}",
            self.delete_message,
            methods=["DELETE"],
            response_model=HttpMessageResponse,
            summary="Удалить сообщение (автор или OWNER/ADMIN чата)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}/reactions",
            self.add_reaction,
            methods=["POST"],
            response_model=HttpMessageResponse,
            summary="Добавить реакцию",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}/reactions/{emoji}",
            self.remove_reaction,
            methods=["DELETE"],
            response_model=HttpMessageResponse,
            summary="Снять реакцию",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}/attachments",
            self.add_attachment,
            methods=["POST"],
            response_model=SuccessResponse[AttachmentResponse],
            status_code=201,
            summary="Добавить вложение (автор)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/messages/{message_id}/attachments/{attachment_id}",
            self.remove_attachment,
            methods=["DELETE"],
            response_model=HttpMessageResponse,
            summary="Удалить вложение (автор)",
            responses=unauth,
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def send_message(
        self,
        chat_id: str,
        body: SendMessageRequest,
        user_id: str = Depends(get_current_user_id),
        chat_repo=Depends(get_chat_repository),
        message_repo=Depends(get_message_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[MessageResponse]:
        handler = SendMessageHandler(
            chat_repo=chat_repo,
            message_repo=message_repo,
            event_bus=event_bus,
        )
        dto = await handler.handle(
            SendMessageCommand(
                caller_id=user_id,
                chat_id=chat_id,
                content=body.content,
                content_format=body.content_format,
                thread_id=body.thread_id,
                reply_to_id=body.reply_to_id,
                message_type=body.message_type,
            )
        )
        return SuccessResponse(data=MessageResponse.model_validate(dto.model_dump()))

    async def list_messages(
        self,
        chat_id: str,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=200),
        include_deleted: bool = Query(default=False),
        user_id: str = Depends(get_current_user_id),
        chat_repo=Depends(get_chat_repository),
        message_repo=Depends(get_message_repository),
    ) -> SuccessResponse[MessageListResponse]:
        handler = GetMessagesByChatHandler(
            chat_repo=chat_repo,
            message_repo=message_repo,
        )
        dto = await handler.handle(
            GetMessagesByChatQuery(
                chat_id=chat_id,
                caller_id=user_id,
                offset=offset,
                limit=limit,
                include_deleted=include_deleted,
            )
        )
        return SuccessResponse(data=MessageListResponse.model_validate(dto.model_dump()))

    async def list_thread_messages(
        self,
        chat_id: str,
        thread_id: str,
        include_deleted: bool = Query(default=False),
        user_id: str = Depends(get_current_user_id),
        chat_repo=Depends(get_chat_repository),
        message_repo=Depends(get_message_repository),
    ) -> SuccessResponse[MessageListResponse]:
        handler = GetThreadMessagesHandler(
            chat_repo=chat_repo,
            message_repo=message_repo,
        )
        dto = await handler.handle(
            GetThreadMessagesQuery(
                chat_id=chat_id,
                thread_id=thread_id,
                caller_id=user_id,
                include_deleted=include_deleted,
            )
        )
        return SuccessResponse(data=MessageListResponse.model_validate(dto.model_dump()))

    async def update_message(
        self,
        message_id: str,
        body: UpdateMessageRequest,
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[MessageResponse]:
        handler = UpdateMessageHandler(message_repo=message_repo, event_bus=event_bus)
        dto = await handler.handle(
            UpdateMessageCommand(
                caller_id=user_id,
                message_id=message_id,
                content=body.content,
                content_format=body.content_format,
            )
        )
        return SuccessResponse(data=MessageResponse.model_validate(dto.model_dump()))

    async def delete_message(
        self,
        message_id: str,
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        chat_repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> HttpMessageResponse:
        handler = DeleteMessageHandler(
            message_repo=message_repo,
            chat_repo=chat_repo,
            event_bus=event_bus,
        )
        await handler.handle(
            DeleteMessageCommand(caller_id=user_id, message_id=message_id)
        )
        return HttpMessageResponse(data=MessageData(message="Сообщение удалено"))

    async def add_reaction(
        self,
        message_id: str,
        body: AddMessageReactionRequest,
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        chat_repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> HttpMessageResponse:
        handler = AddMessageReactionHandler(
            message_repo=message_repo,
            chat_repo=chat_repo,
            event_bus=event_bus,
        )
        await handler.handle(
            AddMessageReactionCommand(
                caller_id=user_id,
                message_id=message_id,
                emoji=body.emoji,
            )
        )
        return HttpMessageResponse(data=MessageData(message="Реакция добавлена"))

    async def remove_reaction(
        self,
        message_id: str,
        emoji: str,
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        chat_repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> HttpMessageResponse:
        handler = RemoveMessageReactionHandler(
            message_repo=message_repo,
            chat_repo=chat_repo,
            event_bus=event_bus,
        )
        await handler.handle(
            RemoveMessageReactionCommand(
                caller_id=user_id,
                message_id=message_id,
                emoji=emoji,
            )
        )
        return HttpMessageResponse(data=MessageData(message="Реакция снята"))

    async def add_attachment(
        self,
        message_id: str,
        file: UploadFile = File(..., description="Файл вложения"),
        attachment_type: str = Form(default="file"),
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        chat_repo=Depends(get_chat_repository),
        file_repo=Depends(get_file_repository),
        file_attachment_port=Depends(get_communication_file_attachment_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[AttachmentResponse]:
        file_data = await file.read()
        handler = AddMessageAttachmentHandler(
            message_repo=message_repo,
            chat_repo=chat_repo,
            file_repo=file_repo,
            file_attachment_port=file_attachment_port,
            event_bus=event_bus,
        )
        dto = await handler.handle(
            AddMessageAttachmentCommand(
                caller_id=user_id,
                message_id=message_id,
                filename=file.filename or "unnamed",
                file_data=file_data,
                content_type=file.content_type or "application/octet-stream",
                attachment_type=attachment_type,
            )
        )
        return SuccessResponse(data=AttachmentResponse.model_validate(dto.model_dump()))

    async def remove_attachment(
        self,
        message_id: str,
        attachment_id: str,
        user_id: str = Depends(get_current_user_id),
        message_repo=Depends(get_message_repository),
        file_attachment_port=Depends(get_communication_file_attachment_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> HttpMessageResponse:
        handler = RemoveMessageAttachmentHandler(
            message_repo=message_repo,
            file_attachment_port=file_attachment_port,
            event_bus=event_bus,
        )
        await handler.handle(
            RemoveMessageAttachmentCommand(
                caller_id=user_id,
                message_id=message_id,
                attachment_id=attachment_id,
            )
        )
        return HttpMessageResponse(data=MessageData(message="Вложение удалено"))
