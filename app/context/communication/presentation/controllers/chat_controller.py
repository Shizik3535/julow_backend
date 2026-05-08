from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.communication.application.commands.archive_chat import (
    ArchiveChatCommand,
    ArchiveChatHandler,
    RestoreChatCommand,
    RestoreChatHandler,
)
from app.context.communication.application.commands.create_chat import (
    CreateAnnouncementCommand,
    CreateAnnouncementHandler,
    CreateChannelCommand,
    CreateChannelHandler,
    CreateDMCommand,
    CreateDMHandler,
    CreateGroupChatCommand,
    CreateGroupChatHandler,
)
from app.context.communication.application.commands.manage_chat_member import (
    AddChatMemberCommand,
    AddChatMemberHandler,
    ChangeChatMemberRoleCommand,
    ChangeChatMemberRoleHandler,
    RemoveChatMemberCommand,
    RemoveChatMemberHandler,
)
from app.context.communication.application.commands.manage_thread import (
    CreateThreadCommand,
    CreateThreadHandler,
    ReopenThreadCommand,
    ReopenThreadHandler,
    ResolveThreadCommand,
    ResolveThreadHandler,
)
from app.context.communication.application.commands.mark_chat_as_read import (
    MarkChatAsReadCommand,
    MarkChatAsReadHandler,
)
from app.context.communication.application.commands.update_chat import (
    UpdateChatInfoCommand,
    UpdateChatInfoHandler,
)
from app.context.communication.application.queries.count_unread_messages import (
    CountUnreadMessagesHandler,
    CountUnreadMessagesQuery,
)
from app.context.communication.application.queries.get_chat import (
    GetChatHandler,
    GetChatQuery,
)
from app.context.communication.application.queries.get_my_chats import (
    GetMyChatsHandler,
    GetMyChatsQuery,
)
from app.context.communication.presentation.dependencies import (
    get_chat_repository,
    get_communication_event_bus,
    get_current_user_id,
    get_message_repository,
)
from app.context.communication.presentation.schemas.requests.create_chat_requests import (
    AddChatMemberRequest,
    ChangeChatMemberRoleRequest,
    CreateAnnouncementRequest,
    CreateChannelRequest,
    CreateDMRequest,
    CreateGroupChatRequest,
    CreateThreadRequest,
    UpdateChatInfoRequest,
)
from app.context.communication.presentation.schemas.responses.chat_response import (
    ChatListResponse,
    ChatResponse,
    ThreadResponse,
)


class ChatController(BaseController):
    """
    Контроллер чатов (Communication BC).

    Endpoint'ы (REST, префикс ``/chats``):
        POST   /chats/dm                                   — создать/получить DM
        POST   /chats/group                                — создать групповой чат
        POST   /chats/channel                              — создать публичный канал
        POST   /chats/announcement                         — создать канал объявлений
        GET    /chats                                      — мои чаты
        GET    /chats/{id}                                 — данные чата
        PATCH  /chats/{id}                                 — обновить (OWNER/ADMIN)
        POST   /chats/{id}/archive                         — архивировать (OWNER)
        POST   /chats/{id}/restore                         — восстановить (OWNER)
        POST   /chats/{id}/read                            — отметить прочитанным
        GET    /chats/{id}/unread-count                    — счётчик непрочитанных
        POST   /chats/{id}/members                         — добавить участника (OWNER/ADMIN)
        DELETE /chats/{id}/members/{user_id}               — удалить (OWNER/ADMIN или self-leave)
        PATCH  /chats/{id}/members/{user_id}/role          — сменить роль (OWNER)
        POST   /chats/{id}/threads                         — создать тред
        POST   /chats/{id}/threads/{thread_id}/resolve     — закрыть тред
        POST   /chats/{id}/threads/{thread_id}/reopen      — открыть тред заново
    """

    def __init__(self) -> None:
        super().__init__(prefix="/chats", tags=["Chats"])

    def _register_routes(self) -> None:
        unauth = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse}
        }

        self._router.add_api_route(
            "/dm",
            self.create_dm,
            methods=["POST"],
            response_model=SuccessResponse[ChatResponse],
            status_code=201,
            summary="Создать или получить DM",
            description=(
                "Идемпотентно: если DM между текущим пользователем и `other_user_id` "
                "уже существует, возвращает его."
            ),
            responses=unauth,
        )
        self._router.add_api_route(
            "/group",
            self.create_group,
            methods=["POST"],
            response_model=SuccessResponse[ChatResponse],
            status_code=201,
            summary="Создать групповой чат",
            responses=unauth,
        )
        self._router.add_api_route(
            "/channel",
            self.create_channel,
            methods=["POST"],
            response_model=SuccessResponse[ChatResponse],
            status_code=201,
            summary="Создать канал в workspace",
            responses=unauth,
        )
        self._router.add_api_route(
            "/announcement",
            self.create_announcement,
            methods=["POST"],
            response_model=SuccessResponse[ChatResponse],
            status_code=201,
            summary="Создать канал объявлений",
            responses=unauth,
        )
        self._router.add_api_route(
            "/",
            self.list_my_chats,
            methods=["GET"],
            response_model=SuccessResponse[ChatListResponse],
            summary="Мои чаты",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}",
            self.get_chat,
            methods=["GET"],
            response_model=SuccessResponse[ChatResponse],
            summary="Получить чат",
            responses={**unauth, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{chat_id}",
            self.update_chat,
            methods=["PATCH"],
            response_model=SuccessResponse[ChatResponse],
            summary="Обновить чат (OWNER/ADMIN)",
            responses={**unauth, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{chat_id}/archive",
            self.archive_chat,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Архивировать чат (OWNER)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/restore",
            self.restore_chat,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Восстановить чат (OWNER)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/read",
            self.mark_as_read,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отметить чат прочитанным",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/unread-count",
            self.unread_count,
            methods=["GET"],
            response_model=SuccessResponse[dict],
            summary="Количество непрочитанных",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/members",
            self.add_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить участника (OWNER/ADMIN)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/members/{user_id}",
            self.remove_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника или выйти из чата",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/members/{user_id}/role",
            self.change_member_role,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Изменить роль участника (OWNER)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/threads",
            self.create_thread,
            methods=["POST"],
            response_model=SuccessResponse[ThreadResponse],
            status_code=201,
            summary="Создать тред",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/threads/{thread_id}/resolve",
            self.resolve_thread,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Закрыть тред",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{chat_id}/threads/{thread_id}/reopen",
            self.reopen_thread,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Открыть тред заново",
            responses=unauth,
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def create_dm(
        self,
        body: CreateDMRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ChatResponse]:
        handler = CreateDMHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            CreateDMCommand(caller_id=user_id, other_user_id=body.other_user_id)
        )
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def create_group(
        self,
        body: CreateGroupChatRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ChatResponse]:
        handler = CreateGroupChatHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            CreateGroupChatCommand(caller_id=user_id, name=body.name)
        )
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def create_channel(
        self,
        body: CreateChannelRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ChatResponse]:
        handler = CreateChannelHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            CreateChannelCommand(
                caller_id=user_id,
                name=body.name,
                workspace_id=body.workspace_id,
            )
        )
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def create_announcement(
        self,
        body: CreateAnnouncementRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ChatResponse]:
        handler = CreateAnnouncementHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            CreateAnnouncementCommand(
                caller_id=user_id,
                name=body.name,
                workspace_id=body.workspace_id,
            )
        )
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def list_my_chats(
        self,
        include_archived: bool = Query(default=False),
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
    ) -> SuccessResponse[ChatListResponse]:
        handler = GetMyChatsHandler(chat_repo=repo)
        dto = await handler.handle(
            GetMyChatsQuery(caller_id=user_id, include_archived=include_archived)
        )
        return SuccessResponse(data=ChatListResponse.model_validate(dto.model_dump()))

    async def get_chat(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
    ) -> SuccessResponse[ChatResponse]:
        handler = GetChatHandler(chat_repo=repo)
        dto = await handler.handle(GetChatQuery(chat_id=chat_id, caller_id=user_id))
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def update_chat(
        self,
        chat_id: str,
        body: UpdateChatInfoRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ChatResponse]:
        handler = UpdateChatInfoHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            UpdateChatInfoCommand(
                caller_id=user_id,
                chat_id=chat_id,
                name=body.name,
                description=body.description,
                icon=body.icon,
                color=body.color,
            )
        )
        return SuccessResponse(data=ChatResponse.model_validate(dto.model_dump()))

    async def archive_chat(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = ArchiveChatHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            ArchiveChatCommand(caller_id=user_id, chat_id=chat_id)
        )
        return MessageResponse(data=MessageData(message="Чат архивирован"))

    async def restore_chat(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RestoreChatHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            RestoreChatCommand(caller_id=user_id, chat_id=chat_id)
        )
        return MessageResponse(data=MessageData(message="Чат восстановлен"))

    async def mark_as_read(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = MarkChatAsReadHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            MarkChatAsReadCommand(caller_id=user_id, chat_id=chat_id)
        )
        return MessageResponse(data=MessageData(message="Чат отмечен прочитанным"))

    async def unread_count(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        chat_repo=Depends(get_chat_repository),
        message_repo=Depends(get_message_repository),
    ) -> SuccessResponse[dict]:
        handler = CountUnreadMessagesHandler(
            chat_repo=chat_repo,
            message_repo=message_repo,
        )
        count = await handler.handle(
            CountUnreadMessagesQuery(chat_id=chat_id, caller_id=user_id)
        )
        return SuccessResponse(data={"unread_count": count})

    async def add_member(
        self,
        chat_id: str,
        body: AddChatMemberRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = AddChatMemberHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            AddChatMemberCommand(
                caller_id=user_id,
                chat_id=chat_id,
                user_id=body.user_id,
            )
        )
        return MessageResponse(data=MessageData(message="Участник добавлен"))

    async def remove_member(
        self,
        chat_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RemoveChatMemberHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            RemoveChatMemberCommand(
                caller_id=caller_id,
                chat_id=chat_id,
                user_id=user_id,
            )
        )
        return MessageResponse(data=MessageData(message="Участник удалён"))

    async def change_member_role(
        self,
        chat_id: str,
        user_id: str,
        body: ChangeChatMemberRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = ChangeChatMemberRoleHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            ChangeChatMemberRoleCommand(
                caller_id=caller_id,
                chat_id=chat_id,
                user_id=user_id,
                new_role=body.role,
            )
        )
        return MessageResponse(data=MessageData(message="Роль изменена"))

    async def create_thread(
        self,
        chat_id: str,
        body: CreateThreadRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[ThreadResponse]:
        handler = CreateThreadHandler(chat_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            CreateThreadCommand(
                caller_id=user_id,
                chat_id=chat_id,
                parent_message_id=body.parent_message_id,
                title=body.title,
            )
        )
        return SuccessResponse(data=ThreadResponse.model_validate(dto.model_dump()))

    async def resolve_thread(
        self,
        chat_id: str,
        thread_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = ResolveThreadHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            ResolveThreadCommand(
                caller_id=user_id,
                chat_id=chat_id,
                thread_id=thread_id,
            )
        )
        return MessageResponse(data=MessageData(message="Тред закрыт"))

    async def reopen_thread(
        self,
        chat_id: str,
        thread_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_chat_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = ReopenThreadHandler(chat_repo=repo, event_bus=event_bus)
        await handler.handle(
            ReopenThreadCommand(
                caller_id=user_id,
                chat_id=chat_id,
                thread_id=thread_id,
            )
        )
        return MessageResponse(data=MessageData(message="Тред открыт заново"))
