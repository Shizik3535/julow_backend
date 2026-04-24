from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.communication.domain.value_objects.chat_member_role import ChatMemberRole


@dataclass(frozen=True)
class ChatCreated(BaseDomainEvent):
    """Чат создан."""

    chat_id: str = ""
    chat_type: ChatType = ChatType.DM


@dataclass(frozen=True)
class ChatUpdated(BaseDomainEvent):
    """Чат обновлён."""

    chat_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ChatMemberAdded(BaseDomainEvent):
    """Участник добавлен в чат."""

    chat_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ChatMemberRemoved(BaseDomainEvent):
    """Участник удалён из чата."""

    chat_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ChatMemberRoleChanged(BaseDomainEvent):
    """Роль участника изменена."""

    chat_id: str = ""
    user_id: str = ""
    new_role: ChatMemberRole = ChatMemberRole.MEMBER


@dataclass(frozen=True)
class ThreadCreated(BaseDomainEvent):
    """Тред создан."""

    thread_id: str = ""
    chat_id: str = ""
    parent_message_id: str = ""


@dataclass(frozen=True)
class ThreadResolved(BaseDomainEvent):
    """Тред закрыт."""

    thread_id: str = ""


@dataclass(frozen=True)
class ThreadReopened(BaseDomainEvent):
    """Тред открыт заново."""

    thread_id: str = ""
