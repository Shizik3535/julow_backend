"""Хелперы преобразования доменных объектов Communication BC в DTO."""
from __future__ import annotations

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.chat_dto import (
    ChatDTO,
    ChatMemberDTO,
    ThreadDTO,
)
from app.context.communication.application.dto.comment_dto import CommentDTO
from app.context.communication.application.dto.meeting_dto import (
    MeetingActionItemDTO,
    MeetingDTO,
    MeetingNoteDTO,
    MeetingParticipantDTO,
    RecurrenceConfigDTO,
)
from app.context.communication.application.dto.message_dto import MessageDTO
from app.context.communication.application.dto.reaction_dto import ReactionDTO
from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.aggregates.comment import Comment
from app.context.communication.domain.aggregates.meeting import Meeting
from app.context.communication.domain.aggregates.message import Message
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.entities.chat_member import ChatMember
from app.context.communication.domain.entities.meeting_action_item import (
    MeetingActionItem,
)
from app.context.communication.domain.entities.meeting_note import MeetingNote
from app.context.communication.domain.entities.meeting_participant import (
    MeetingParticipant,
)
from app.context.communication.domain.entities.reaction import Reaction
from app.context.communication.domain.entities.thread import Thread


def reaction_to_dto(reaction: Reaction) -> ReactionDTO:
    """Преобразует Reaction в ReactionDTO."""
    return ReactionDTO(
        user_id=str(reaction.user_id),
        emoji=str(reaction.emoji),
        created_at=reaction.created_at,
    )


def attachment_to_dto(attachment: Attachment) -> AttachmentDTO:
    """Преобразует Attachment в AttachmentDTO."""
    return AttachmentDTO(
        id=str(attachment.id),
        file_id=str(attachment.file_id),
        url=str(attachment.url) if attachment.url else None,
        attachment_type=attachment.attachment_type.value,
        name=attachment.name,
        size_bytes=attachment.size_bytes,
        preview_url=str(attachment.preview_url) if attachment.preview_url else None,
        created_at=attachment.created_at,
    )


def chat_member_to_dto(member: ChatMember) -> ChatMemberDTO:
    """Преобразует ChatMember в ChatMemberDTO."""
    return ChatMemberDTO(
        user_id=str(member.user_id),
        role=member.role.value,
        joined_at=member.joined_at,
        last_read_at=member.last_read_at,
    )


def thread_to_dto(thread: Thread) -> ThreadDTO:
    """Преобразует Thread в ThreadDTO."""
    return ThreadDTO(
        id=str(thread.id),
        parent_message_id=str(thread.parent_message_id),
        title=thread.title,
        is_resolved=thread.is_resolved,
        created_at=thread.created_at,
    )


def chat_to_dto(chat: Chat) -> ChatDTO:
    """Преобразует агрегат Chat в ChatDTO."""
    return ChatDTO(
        id=str(chat.id),
        chat_type=chat.chat_type.value,
        name=chat.name,
        description=chat.description,
        icon=chat.icon,
        color=chat.color.value if chat.color else None,
        workspace_id=str(chat.workspace_id) if chat.workspace_id else None,
        project_id=str(chat.project_id) if chat.project_id else None,
        members=[chat_member_to_dto(m) for m in chat.members],
        threads=[thread_to_dto(t) for t in chat.threads],
        last_message_at=chat.last_message_at,
        is_archived=chat.is_archived,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


def message_to_dto(message: Message) -> MessageDTO:
    """Преобразует агрегат Message в MessageDTO."""
    return MessageDTO(
        id=str(message.id),
        chat_id=str(message.chat_id),
        thread_id=str(message.thread_id) if message.thread_id else None,
        sender_id=str(message.sender_id),
        content=message.content.content if message.content else None,
        content_format=(
            message.content.format.value if message.content else "markdown"
        ),
        message_type=message.message_type.value,
        reply_to_id=str(message.reply_to_id) if message.reply_to_id else None,
        attachments=[attachment_to_dto(a) for a in message.attachments],
        reactions=[reaction_to_dto(r) for r in message.reactions],
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
        updated_at=message.updated_at,
    )


def meeting_participant_to_dto(p: MeetingParticipant) -> MeetingParticipantDTO:
    return MeetingParticipantDTO(
        user_id=str(p.user_id),
        is_mandatory=p.is_mandatory,
        rsvp_status=p.rsvp_status.value,
        joined_at=p.joined_at,
    )


def meeting_note_to_dto(n: MeetingNote) -> MeetingNoteDTO:
    return MeetingNoteDTO(
        id=str(n.id),
        author_id=str(n.author_id),
        content=n.content.content if n.content else None,
        content_format=n.content.format.value if n.content else "markdown",
        created_at=n.created_at,
    )


def meeting_action_item_to_dto(ai: MeetingActionItem) -> MeetingActionItemDTO:
    return MeetingActionItemDTO(
        id=str(ai.id),
        text=ai.text,
        assignee_id=str(ai.assignee_id) if ai.assignee_id else None,
        due_date=ai.due_date,
        is_completed=ai.is_completed,
    )


def meeting_to_dto(meeting: Meeting) -> MeetingDTO:
    """Преобразует агрегат Meeting в MeetingDTO."""
    recurrence_dto: RecurrenceConfigDTO | None = None
    if meeting.recurrence is not None:
        recurrence_dto = RecurrenceConfigDTO(
            pattern=meeting.recurrence.pattern.value,
            interval=meeting.recurrence.interval,
            end_date=meeting.recurrence.end_date,
            max_occurrences=meeting.recurrence.max_occurrences,
        )
    return MeetingDTO(
        id=str(meeting.id),
        title=meeting.title,
        description=meeting.description.content if meeting.description else None,
        description_format=(
            meeting.description.format.value if meeting.description else "markdown"
        ),
        meeting_type=meeting.meeting_type.value,
        status=meeting.status.value,
        scheduled_at=meeting.scheduled_at,
        duration_minutes=meeting.duration_minutes,
        location=meeting.location,
        conference_provider=meeting.conference_provider.value,
        conference_url=str(meeting.conference_url) if meeting.conference_url else None,
        conference_room_id=meeting.conference_room_id,
        project_id=str(meeting.project_id) if meeting.project_id else None,
        workspace_id=str(meeting.workspace_id),
        organizer_id=str(meeting.organizer_id),
        participants=[meeting_participant_to_dto(p) for p in meeting.participants],
        notes=[meeting_note_to_dto(n) for n in meeting.notes],
        action_items=[meeting_action_item_to_dto(ai) for ai in meeting.action_items],
        recurrence=recurrence_dto,
        agenda=[item.text for item in (meeting.agenda.items if meeting.agenda else [])],
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


def comment_to_dto(comment: Comment) -> CommentDTO:
    """Преобразует агрегат Comment в CommentDTO."""
    return CommentDTO(
        id=str(comment.id),
        author_id=str(comment.author_id),
        target_type=comment.target_type.value,
        target_id=str(comment.target_id),
        content=comment.content.content if comment.content else None,
        content_format=(
            comment.content.format.value if comment.content else "markdown"
        ),
        parent_comment_id=(
            str(comment.parent_comment_id) if comment.parent_comment_id else None
        ),
        attachments=[attachment_to_dto(a) for a in comment.attachments],
        reactions=[reaction_to_dto(r) for r in comment.reactions],
        is_pinned=comment.is_pinned,
        is_system=comment.is_system,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )
