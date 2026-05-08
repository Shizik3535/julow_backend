from __future__ import annotations

from fastapi import Depends, File, Form, Query, UploadFile

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.communication.application.commands.add_comment import (
    AddCommentCommand,
    AddCommentHandler,
)
from app.context.communication.application.commands.delete_comment import (
    DeleteCommentCommand,
    DeleteCommentHandler,
)
from app.context.communication.application.commands.manage_comment_attachment import (
    AddCommentAttachmentCommand,
    AddCommentAttachmentHandler,
    RemoveCommentAttachmentCommand,
    RemoveCommentAttachmentHandler,
)
from app.context.communication.application.commands.manage_comment_reaction import (
    AddCommentReactionCommand,
    AddCommentReactionHandler,
    RemoveCommentReactionCommand,
    RemoveCommentReactionHandler,
)
from app.context.communication.application.commands.pin_comment import (
    PinCommentCommand,
    PinCommentHandler,
    UnpinCommentCommand,
    UnpinCommentHandler,
)
from app.context.communication.application.commands.update_comment import (
    UpdateCommentCommand,
    UpdateCommentHandler,
)
from app.context.communication.application.queries.get_comment import (
    GetCommentHandler,
    GetCommentQuery,
)
from app.context.communication.application.queries.get_comment_replies import (
    GetCommentRepliesHandler,
    GetCommentRepliesQuery,
)
from app.context.communication.application.queries.get_comments_by_target import (
    GetCommentsByTargetHandler,
    GetCommentsByTargetQuery,
)
from app.context.communication.presentation.dependencies import (
    get_comment_repository,
    get_comment_target_access_port,
    get_communication_event_bus,
    get_communication_file_attachment_port,
    get_current_user_id,
)
from app.context.communication.presentation.schemas.requests.add_comment_reaction_request import (
    AddCommentReactionRequest,
)
from app.context.communication.presentation.schemas.requests.add_comment_request import (
    AddCommentRequest,
)
from app.context.communication.presentation.schemas.requests.update_comment_request import (
    UpdateCommentRequest,
)
from app.context.communication.presentation.schemas.responses.attachment_response import (
    AttachmentResponse,
)
from app.context.communication.presentation.schemas.responses.comment_list_response import (
    CommentListResponse,
)
from app.context.communication.presentation.schemas.responses.comment_response import (
    CommentResponse,
)


class CommentController(BaseController):
    """
    Контроллер комментариев (Communication BC).

    Endpoint'ы (REST, префикс ``/comments``):
        POST   /comments                                    — создать комментарий
        GET    /comments                                    — комментарии по target
        GET    /comments/{id}                               — получить комментарий
        PATCH  /comments/{id}                               — обновить контент
        DELETE /comments/{id}                               — soft-delete
        GET    /comments/{id}/replies                       — ответы на комментарий
        POST   /comments/{id}/pin                           — закрепить
        POST   /comments/{id}/unpin                         — открепить
        POST   /comments/{id}/reactions                     — добавить реакцию
        DELETE /comments/{id}/reactions/{emoji}             — снять реакцию
        POST   /comments/{id}/attachments                   — добавить вложение
        DELETE /comments/{id}/attachments/{attachment_id}   — удалить вложение
    """

    def __init__(self) -> None:
        super().__init__(prefix="/comments", tags=["Comments"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/",
            self.add_comment,
            methods=["POST"],
            response_model=SuccessResponse[CommentResponse],
            status_code=201,
            summary="Создать комментарий",
            description=(
                "Создаёт комментарий к произвольной сущности (task/project/...). "
                "Если указан `parent_comment_id` — создаёт ответ."
            ),
            responses={
                201: {"description": "Комментарий создан"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Родительский комментарий не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/",
            self.list_comments,
            methods=["GET"],
            response_model=SuccessResponse[CommentListResponse],
            summary="Список комментариев по target",
            description="Возвращает комментарии по `target_type` + `target_id`.",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{comment_id}",
            self.get_comment,
            methods=["GET"],
            response_model=SuccessResponse[CommentResponse],
            summary="Получить комментарий",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Комментарий не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{comment_id}",
            self.update_comment,
            methods=["PATCH"],
            response_model=SuccessResponse[CommentResponse],
            summary="Обновить комментарий",
            description="Обновить может только автор. Системные/удалённые редактировать нельзя.",
            responses={
                200: {"description": "Обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Комментарий не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{comment_id}",
            self.delete_comment,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить комментарий (soft)",
            description="Удалить может только автор. Системный комментарий удалить нельзя.",
            responses={
                200: {"description": "Удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Комментарий не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{comment_id}/replies",
            self.get_replies,
            methods=["GET"],
            response_model=SuccessResponse[CommentListResponse],
            summary="Получить ответы на комментарий",
        )
        self._router.add_api_route(
            "/{comment_id}/pin",
            self.pin_comment,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Закрепить комментарий",
        )
        self._router.add_api_route(
            "/{comment_id}/unpin",
            self.unpin_comment,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Открепить комментарий",
        )
        self._router.add_api_route(
            "/{comment_id}/reactions",
            self.add_reaction,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить реакцию",
        )
        self._router.add_api_route(
            "/{comment_id}/reactions/{emoji}",
            self.remove_reaction,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Снять реакцию",
        )
        self._router.add_api_route(
            "/{comment_id}/attachments",
            self.add_attachment,
            methods=["POST"],
            response_model=SuccessResponse[AttachmentResponse],
            status_code=201,
            summary="Добавить вложение",
        )
        self._router.add_api_route(
            "/{comment_id}/attachments/{attachment_id}",
            self.remove_attachment,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить вложение",
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def add_comment(
        self,
        body: AddCommentRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[CommentResponse]:
        handler = AddCommentHandler(
            comment_repo=repo,
            target_access=target_access,
            event_bus=event_bus,
        )
        command = AddCommentCommand(
            author_id=user_id,
            target_type=body.target_type,
            target_id=body.target_id,
            content=body.content,
            content_format=body.content_format,
            parent_comment_id=body.parent_comment_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=CommentResponse.model_validate(dto.model_dump()))

    async def list_comments(
        self,
        target_type: str = Query(..., description="Тип комментируемой сущности"),
        target_id: str = Query(..., description="UUID комментируемой сущности"),
        include_deleted: bool = Query(default=False, description="Включать soft-deleted"),
        only_root: bool = Query(default=False, description="Только корневые"),
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
    ) -> SuccessResponse[CommentListResponse]:
        handler = GetCommentsByTargetHandler(
            comment_repo=repo,
            target_access=target_access,
        )
        query = GetCommentsByTargetQuery(
            target_type=target_type,
            target_id=target_id,
            caller_id=user_id,
            include_deleted=include_deleted,
            only_root=only_root,
        )
        dto = await handler.handle(query)
        return SuccessResponse(data=CommentListResponse.model_validate(dto.model_dump()))

    async def get_comment(
        self,
        comment_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
    ) -> SuccessResponse[CommentResponse]:
        handler = GetCommentHandler(
            comment_repo=repo,
            target_access=target_access,
        )
        dto = await handler.handle(
            GetCommentQuery(comment_id=comment_id, caller_id=user_id)
        )
        return SuccessResponse(data=CommentResponse.model_validate(dto.model_dump()))

    async def update_comment(
        self,
        comment_id: str,
        body: UpdateCommentRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[CommentResponse]:
        handler = UpdateCommentHandler(comment_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            UpdateCommentCommand(
                comment_id=comment_id,
                caller_id=user_id,
                content=body.content,
                content_format=body.content_format,
            )
        )
        return SuccessResponse(data=CommentResponse.model_validate(dto.model_dump()))

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = DeleteCommentHandler(comment_repo=repo, event_bus=event_bus)
        await handler.handle(
            DeleteCommentCommand(comment_id=comment_id, caller_id=user_id)
        )
        return MessageResponse(data=MessageData(message="Комментарий удалён"))

    async def get_replies(
        self,
        comment_id: str,
        include_deleted: bool = Query(default=False),
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
    ) -> SuccessResponse[CommentListResponse]:
        handler = GetCommentRepliesHandler(
            comment_repo=repo,
            target_access=target_access,
        )
        dto = await handler.handle(
            GetCommentRepliesQuery(
                comment_id=comment_id,
                caller_id=user_id,
                include_deleted=include_deleted,
            )
        )
        return SuccessResponse(data=CommentListResponse.model_validate(dto.model_dump()))

    async def pin_comment(
        self,
        comment_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = PinCommentHandler(
            comment_repo=repo,
            target_access=target_access,
            event_bus=event_bus,
        )
        await handler.handle(
            PinCommentCommand(comment_id=comment_id, caller_id=user_id)
        )
        return MessageResponse(data=MessageData(message="Комментарий закреплён"))

    async def unpin_comment(
        self,
        comment_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = UnpinCommentHandler(
            comment_repo=repo,
            target_access=target_access,
            event_bus=event_bus,
        )
        await handler.handle(
            UnpinCommentCommand(comment_id=comment_id, caller_id=user_id)
        )
        return MessageResponse(data=MessageData(message="Комментарий откреплён"))

    async def add_reaction(
        self,
        comment_id: str,
        body: AddCommentReactionRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = AddCommentReactionHandler(
            comment_repo=repo,
            target_access=target_access,
            event_bus=event_bus,
        )
        await handler.handle(
            AddCommentReactionCommand(
                comment_id=comment_id,
                user_id=user_id,
                emoji=body.emoji,
            )
        )
        return MessageResponse(data=MessageData(message="Реакция добавлена"))

    async def remove_reaction(
        self,
        comment_id: str,
        emoji: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RemoveCommentReactionHandler(
            comment_repo=repo,
            target_access=target_access,
            event_bus=event_bus,
        )
        await handler.handle(
            RemoveCommentReactionCommand(
                comment_id=comment_id,
                user_id=user_id,
                emoji=emoji,
            )
        )
        return MessageResponse(data=MessageData(message="Реакция снята"))

    async def add_attachment(
        self,
        comment_id: str,
        file: UploadFile = File(..., description="Файл вложения"),
        attachment_type: str = Form(
            default="file",
            description="Тип вложения (image/video/file/link/voice)",
        ),
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        file_attachment_port=Depends(get_communication_file_attachment_port),
        target_access=Depends(get_comment_target_access_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[AttachmentResponse]:
        """Загрузить файл и зарегистрировать вложение комментария."""
        file_data = await file.read()
        handler = AddCommentAttachmentHandler(
            comment_repo=repo,
            file_attachment_port=file_attachment_port,
            target_access=target_access,
            event_bus=event_bus,
        )
        dto = await handler.handle(
            AddCommentAttachmentCommand(
                comment_id=comment_id,
                caller_id=user_id,
                filename=file.filename or "unnamed",
                file_data=file_data,
                content_type=file.content_type or "application/octet-stream",
                attachment_type=attachment_type,
            )
        )
        return SuccessResponse(data=AttachmentResponse.model_validate(dto.model_dump()))

    async def remove_attachment(
        self,
        comment_id: str,
        attachment_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_comment_repository),
        file_attachment_port=Depends(get_communication_file_attachment_port),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RemoveCommentAttachmentHandler(
            comment_repo=repo,
            file_attachment_port=file_attachment_port,
            event_bus=event_bus,
        )
        await handler.handle(
            RemoveCommentAttachmentCommand(
                comment_id=comment_id,
                attachment_id=attachment_id,
                caller_id=user_id,
            )
        )
        return MessageResponse(data=MessageData(message="Вложение удалено"))
