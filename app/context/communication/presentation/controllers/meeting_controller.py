from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.communication.application.commands.create_meeting import (
    CreateMeetingCommand,
    CreateMeetingHandler,
)
from app.context.communication.application.commands.join_meeting import (
    JoinMeetingCommand,
    JoinMeetingHandler,
)
from app.context.communication.application.commands.manage_meeting_content import (
    AddActionItemCommand,
    AddActionItemHandler,
    AddMeetingNoteCommand,
    AddMeetingNoteHandler,
    CompleteActionItemCommand,
    CompleteActionItemHandler,
    RemoveActionItemCommand,
    RemoveActionItemHandler,
)
from app.context.communication.application.commands.manage_meeting_participant import (
    AddMeetingParticipantCommand,
    AddMeetingParticipantHandler,
    RemoveMeetingParticipantCommand,
    RemoveMeetingParticipantHandler,
    UpdateRSVPCommand,
    UpdateRSVPHandler,
)
from app.context.communication.application.commands.meeting_lifecycle import (
    CancelMeetingCommand,
    CancelMeetingHandler,
    CompleteMeetingCommand,
    CompleteMeetingHandler,
    StartMeetingCommand,
    StartMeetingHandler,
)
from app.context.communication.application.commands.update_meeting import (
    UpdateMeetingCommand,
    UpdateMeetingHandler,
)
from app.context.communication.application.queries.get_meeting import (
    GetMeetingHandler,
    GetMeetingQuery,
)
from app.context.communication.application.queries.get_meetings_by_workspace import (
    GetMeetingsByProjectHandler,
    GetMeetingsByProjectQuery,
    GetMeetingsByWorkspaceHandler,
    GetMeetingsByWorkspaceQuery,
)
from app.context.communication.application.queries.get_my_meetings import (
    GetMyMeetingsHandler,
    GetMyMeetingsQuery,
)
from app.context.communication.application.exceptions.authorization_exceptions import (
    InsufficientMeetingCreatePermissionsException,
)
from app.context.communication.presentation.dependencies import (
    get_communication_event_bus,
    get_conference_provider_registry,
    get_current_user_id,
    get_meeting_repository,
    get_project_membership_repository,
    get_project_repository,
    get_project_role_repository,
    get_profile_user_provider,
)
from app.context.communication.presentation.schemas.requests.meeting_requests import (
    AddActionItemRequest,
    AddMeetingNoteRequest,
    AddMeetingParticipantRequest,
    CreateMeetingRequest,
    UpdateMeetingRequest,
    UpdateRSVPRequest,
)
from app.context.communication.presentation.schemas.responses.meeting_response import (
    MeetingJoinResponse,
    MeetingListResponse,
    MeetingResponse,
)
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import (
    ProjectRoleRepository,
)
from app.shared.domain.value_objects.id_vo import Id


class MeetingController(BaseController):
    """
    Контроллер совещаний (Communication BC).

    Endpoint'ы (REST, префикс ``/meetings``):
        POST   /meetings                                   — создать совещание
        GET    /meetings                                   — мои предстоящие совещания
        GET    /meetings/by-workspace/{workspace_id}       — совещания workspace (видимые мне)
        GET    /meetings/by-project/{project_id}           — совещания проекта (видимые мне)
        GET    /meetings/{id}                              — данные совещания
        PATCH  /meetings/{id}                              — обновить (organizer)
        POST   /meetings/{id}/start                        — начать (organizer)
        POST   /meetings/{id}/complete                     — завершить (organizer)
        POST   /meetings/{id}/cancel                       — отменить (organizer)
        POST   /meetings/{id}/join                         — получить join_url/token
        POST   /meetings/{id}/participants                 — добавить участника (organizer)
        DELETE /meetings/{id}/participants/{user_id}       — удалить участника (organizer)
        POST   /meetings/{id}/rsvp                         — обновить свой RSVP
        POST   /meetings/{id}/notes                        — добавить заметку (participant)
        POST   /meetings/{id}/action-items                 — добавить action item (participant)
        POST   /meetings/{id}/action-items/{ai_id}/complete— завершить action item
        DELETE /meetings/{id}/action-items/{ai_id}         — удалить action item
    """

    def __init__(self) -> None:
        super().__init__(prefix="/meetings", tags=["Meetings"])

    def _register_routes(self) -> None:
        unauth = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
        }
        fmt = unauth | {403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}

        self._router.add_api_route(
            "/",
            self.create_meeting,
            methods=["POST"],
            response_model=SuccessResponse[MeetingResponse],
            status_code=201,
            summary="Создать совещание",
            description=(
                "Создаёт совещание. Для `conference_provider=manual` требуется "
                "`manual_url`. Для `internal/zoom/telemost/google_meet/teams` "
                "комнату создаёт соответствующий `ConferenceProviderPort`."
            ),
            responses=unauth | {501: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/",
            self.list_my_meetings,
            methods=["GET"],
            response_model=SuccessResponse[MeetingListResponse],
            summary="Мои предстоящие совещания",
            responses=unauth,
        )
        self._router.add_api_route(
            "/by-workspace/{workspace_id}",
            self.list_by_workspace,
            methods=["GET"],
            response_model=SuccessResponse[MeetingListResponse],
            summary="Совещания workspace (видимые мне)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/by-project/{project_id}",
            self.list_by_project,
            methods=["GET"],
            response_model=SuccessResponse[MeetingListResponse],
            summary="Совещания проекта (видимые мне)",
            responses=unauth,
        )
        self._router.add_api_route(
            "/{meeting_id}",
            self.get_meeting,
            methods=["GET"],
            response_model=SuccessResponse[MeetingResponse],
            summary="Получить совещание",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}",
            self.update_meeting,
            methods=["PATCH"],
            response_model=SuccessResponse[MeetingResponse],
            summary="Обновить совещание (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/start",
            self.start_meeting,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Начать совещание (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/complete",
            self.complete_meeting,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Завершить совещание (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/cancel",
            self.cancel_meeting,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Отменить совещание (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/join",
            self.join_meeting,
            methods=["POST"],
            response_model=SuccessResponse[MeetingJoinResponse],
            summary="Получить join_url/access_token для подключения",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/participants",
            self.add_participant,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить участника (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/participants/{user_id}",
            self.remove_participant,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника (организатор)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/rsvp",
            self.update_rsvp,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Обновить свой RSVP-ответ",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/notes",
            self.add_note,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить заметку (участник, на IN_PROGRESS/COMPLETED)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/action-items",
            self.add_action_item,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить action item (участник)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/action-items/{action_item_id}/complete",
            self.complete_action_item,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Завершить action item (участник)",
            responses=fmt,
        )
        self._router.add_api_route(
            "/{meeting_id}/action-items/{action_item_id}",
            self.remove_action_item,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить action item (участник)",
            responses=fmt,
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def create_meeting(
        self,
        body: CreateMeetingRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        project_repo: ProjectRepository = Depends(get_project_repository),
        project_membership_repo: ProjectMembershipRepository = Depends(
            get_project_membership_repository
        ),
        project_role_repo: ProjectRoleRepository = Depends(get_project_role_repository),
        registry=Depends(get_conference_provider_registry),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[MeetingResponse]:
        if body.project_id:
            project = await project_repo.get_by_id(Id.from_string(body.project_id))
            member = await project_membership_repo.get_member_by_project_and_user(
                Id.from_string(body.project_id),
                Id.from_string(user_id),
            )
            is_owner = any(str(owner_id) == user_id for owner_id in (project.owner_ids if project else []))
            if (member is None or not member.is_active) and not is_owner:
                raise InsufficientMeetingCreatePermissionsException(body.project_id)

            if is_owner:
                role_name = "owner"
            else:
                role = await project_role_repo.get_by_id(member.role_id)
                role_name = (getattr(role, "name", "") or "").lower() if role else ""
            if role_name not in {"owner", "admin", "manager"}:
                raise InsufficientMeetingCreatePermissionsException(body.project_id)

        handler = CreateMeetingHandler(
            meeting_repo=repo,
            provider_registry=registry,
            event_bus=event_bus,
        )
        dto = await handler.handle(
            CreateMeetingCommand(
                caller_id=user_id,
                workspace_id=body.workspace_id,
                title=body.title,
                scheduled_at=body.scheduled_at,
                meeting_type=body.meeting_type,
                conference_provider=body.conference_provider,
                manual_url=body.manual_url,
                agenda=body.agenda,
                duration_minutes=body.duration_minutes,
                description=body.description,
                description_format=body.description_format,
                location=body.location,
                project_id=body.project_id,
                participant_ids=body.participant_ids,
                recurrence_pattern=body.recurrence_pattern,
                recurrence_interval=body.recurrence_interval,
            )
        )
        return SuccessResponse(data=MeetingResponse.model_validate(dto.model_dump()))

    async def list_my_meetings(
        self,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
    ) -> SuccessResponse[MeetingListResponse]:
        handler = GetMyMeetingsHandler(meeting_repo=repo)
        dto = await handler.handle(GetMyMeetingsQuery(caller_id=user_id))
        return SuccessResponse(data=MeetingListResponse.model_validate(dto.model_dump()))

    async def list_by_workspace(
        self,
        workspace_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
    ) -> SuccessResponse[MeetingListResponse]:
        handler = GetMeetingsByWorkspaceHandler(meeting_repo=repo)
        dto = await handler.handle(
            GetMeetingsByWorkspaceQuery(workspace_id=workspace_id, caller_id=user_id)
        )
        return SuccessResponse(data=MeetingListResponse.model_validate(dto.model_dump()))

    async def list_by_project(
        self,
        project_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
    ) -> SuccessResponse[MeetingListResponse]:
        handler = GetMeetingsByProjectHandler(meeting_repo=repo)
        dto = await handler.handle(
            GetMeetingsByProjectQuery(project_id=project_id, caller_id=user_id)
        )
        return SuccessResponse(data=MeetingListResponse.model_validate(dto.model_dump()))

    async def get_meeting(
        self,
        meeting_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
    ) -> SuccessResponse[MeetingResponse]:
        handler = GetMeetingHandler(meeting_repo=repo)
        dto = await handler.handle(
            GetMeetingQuery(meeting_id=meeting_id, caller_id=user_id)
        )
        return SuccessResponse(data=MeetingResponse.model_validate(dto.model_dump()))

    async def update_meeting(
        self,
        meeting_id: str,
        body: UpdateMeetingRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> SuccessResponse[MeetingResponse]:
        handler = UpdateMeetingHandler(meeting_repo=repo, event_bus=event_bus)
        dto = await handler.handle(
            UpdateMeetingCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                title=body.title,
                scheduled_at=body.scheduled_at,
                duration_minutes=body.duration_minutes,
                description=body.description,
                description_format=body.description_format,
                location=body.location,
                conference_url=body.conference_url,
                agenda=body.agenda,
            )
        )
        return SuccessResponse(data=MeetingResponse.model_validate(dto.model_dump()))

    async def start_meeting(
        self,
        meeting_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = StartMeetingHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            StartMeetingCommand(caller_id=user_id, meeting_id=meeting_id)
        )
        return MessageResponse(data=MessageData(message="Совещание начато"))

    async def complete_meeting(
        self,
        meeting_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        registry=Depends(get_conference_provider_registry),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = CompleteMeetingHandler(
            meeting_repo=repo,
            provider_registry=registry,
            event_bus=event_bus,
        )
        await handler.handle(
            CompleteMeetingCommand(caller_id=user_id, meeting_id=meeting_id)
        )
        return MessageResponse(data=MessageData(message="Совещание завершено"))

    async def cancel_meeting(
        self,
        meeting_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        registry=Depends(get_conference_provider_registry),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = CancelMeetingHandler(
            meeting_repo=repo,
            provider_registry=registry,
            event_bus=event_bus,
        )
        await handler.handle(
            CancelMeetingCommand(caller_id=user_id, meeting_id=meeting_id)
        )
        return MessageResponse(data=MessageData(message="Совещание отменено"))

    async def join_meeting(
        self,
        meeting_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        registry=Depends(get_conference_provider_registry),
        event_bus=Depends(get_communication_event_bus),
        profile_provider=Depends(get_profile_user_provider),
    ) -> SuccessResponse[MeetingJoinResponse]:
        handler = JoinMeetingHandler(
            meeting_repo=repo,
            provider_registry=registry,
            event_bus=event_bus,
            profile_provider=profile_provider,
        )
        dto = await handler.handle(
            JoinMeetingCommand(caller_id=user_id, meeting_id=meeting_id)
        )
        return SuccessResponse(data=MeetingJoinResponse.model_validate(dto.model_dump()))

    async def add_participant(
        self,
        meeting_id: str,
        body: AddMeetingParticipantRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = AddMeetingParticipantHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            AddMeetingParticipantCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                user_id=body.user_id,
                is_mandatory=body.is_mandatory,
            )
        )
        return MessageResponse(data=MessageData(message="Участник добавлен"))

    async def remove_participant(
        self,
        meeting_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RemoveMeetingParticipantHandler(
            meeting_repo=repo, event_bus=event_bus
        )
        await handler.handle(
            RemoveMeetingParticipantCommand(
                caller_id=caller_id,
                meeting_id=meeting_id,
                user_id=user_id,
            )
        )
        return MessageResponse(data=MessageData(message="Участник удалён"))

    async def update_rsvp(
        self,
        meeting_id: str,
        body: UpdateRSVPRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = UpdateRSVPHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            UpdateRSVPCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                rsvp_status=body.rsvp_status,
            )
        )
        return MessageResponse(data=MessageData(message="RSVP обновлён"))

    async def add_note(
        self,
        meeting_id: str,
        body: AddMeetingNoteRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = AddMeetingNoteHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            AddMeetingNoteCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                content=body.content,
                content_format=body.content_format,
            )
        )
        return MessageResponse(data=MessageData(message="Заметка добавлена"))

    async def add_action_item(
        self,
        meeting_id: str,
        body: AddActionItemRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = AddActionItemHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            AddActionItemCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                text=body.text,
                assignee_id=body.assignee_id,
                due_date=body.due_date,
            )
        )
        return MessageResponse(data=MessageData(message="Action item добавлен"))

    async def complete_action_item(
        self,
        meeting_id: str,
        action_item_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = CompleteActionItemHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            CompleteActionItemCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                action_item_id=action_item_id,
            )
        )
        return MessageResponse(data=MessageData(message="Action item завершён"))

    async def remove_action_item(
        self,
        meeting_id: str,
        action_item_id: str,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_meeting_repository),
        event_bus=Depends(get_communication_event_bus),
    ) -> MessageResponse:
        handler = RemoveActionItemHandler(meeting_repo=repo, event_bus=event_bus)
        await handler.handle(
            RemoveActionItemCommand(
                caller_id=user_id,
                meeting_id=meeting_id,
                action_item_id=action_item_id,
            )
        )
        return MessageResponse(data=MessageData(message="Action item удалён"))
