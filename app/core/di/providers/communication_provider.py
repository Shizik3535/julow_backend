"""DI providers для Communication BC."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)
from app.context.communication.domain.repositories.message_repository import (
    MessageRepository,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)
from app.context.communication.infrastructure.integration.inboard.comment_target_access_adapter import (
    CommentTargetAccessAdapter,
)
from app.context.communication.infrastructure.integration.inboard.conference_provider_registry import (
    ConferenceProviderRegistry,
)
from app.context.communication.infrastructure.integration.inboard.manual_link_conference_adapter import (
    ManualLinkConferenceAdapter,
)
from app.context.communication.infrastructure.persistence.mappers.chat_mapper import (
    ChatMapper,
)
from app.context.communication.infrastructure.persistence.mappers.comment_mapper import (
    CommentMapper,
)
from app.context.communication.infrastructure.persistence.mappers.meeting_mapper import (
    MeetingMapper,
)
from app.context.communication.infrastructure.persistence.mappers.message_mapper import (
    MessageMapper,
)
from app.context.communication.infrastructure.persistence.repositories.sql_chat_repository import (
    SqlChatRepository,
)
from app.context.communication.infrastructure.persistence.repositories.sql_comment_repository import (
    SqlCommentRepository,
)
from app.context.communication.infrastructure.persistence.repositories.sql_meeting_repository import (
    SqlMeetingRepository,
)
from app.context.communication.infrastructure.persistence.repositories.sql_message_repository import (
    SqlMessageRepository,
)
from app.context.project.application.ports.integration.outboard.epic_provider import (
    EpicProvider,
)
from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.task.application.ports.integration.outboard.task_provider import (
    TaskProvider,
)


# --- Mappers ---


def create_comment_mapper() -> CommentMapper:
    """Создать CommentMapper."""
    return CommentMapper()


def create_chat_mapper() -> ChatMapper:
    """Создать ChatMapper."""
    return ChatMapper()


def create_message_mapper() -> MessageMapper:
    """Создать MessageMapper."""
    return MessageMapper()


def create_meeting_mapper() -> MeetingMapper:
    """Создать MeetingMapper."""
    return MeetingMapper()


# --- Repositories ---


def create_comment_repository(
    session: AsyncSession,
    mapper: CommentMapper,
) -> CommentRepository:
    """Создать SqlCommentRepository."""
    return SqlCommentRepository(session=session, mapper=mapper)


def create_chat_repository(
    session: AsyncSession,
    mapper: ChatMapper,
) -> ChatRepository:
    """Создать SqlChatRepository."""
    return SqlChatRepository(session=session, mapper=mapper)


def create_message_repository(
    session: AsyncSession,
    mapper: MessageMapper,
) -> MessageRepository:
    """Создать SqlMessageRepository."""
    return SqlMessageRepository(session=session, mapper=mapper)


def create_meeting_repository(
    session: AsyncSession,
    mapper: MeetingMapper,
) -> MeetingRepository:
    """Создать SqlMeetingRepository."""
    return SqlMeetingRepository(session=session, mapper=mapper)


# --- Conference provider registry ---


def create_conference_provider_registry() -> ConferenceProviderRegistry:
    """Собрать реестр адаптеров ConferenceProviderPort.

    В MVP зарегистрирован только ``MANUAL``. INTERNAL/Zoom/Telemost/...
    будут добавлены по мере реализации соответствующих адаптеров.
    """
    return ConferenceProviderRegistry(
        adapters={
            ConferenceProvider.MANUAL: ManualLinkConferenceAdapter(),
        }
    )


# --- Integration adapters ---


def create_comment_target_access_adapter(
    task_provider: TaskProvider,
    epic_provider: EpicProvider,
    sprint_provider: SprintProvider,
    project_permission_provider: ProjectPermissionProvider,
) -> CommentTargetAccessPort:
    """Создать CommentTargetAccessAdapter."""
    return CommentTargetAccessAdapter(
        task_provider=task_provider,
        epic_provider=epic_provider,
        sprint_provider=sprint_provider,
        project_permission_provider=project_permission_provider,
    )
