from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.communication.domain.value_objects.message_type import MessageType


@dataclass(frozen=True)
class MessageSent(BaseDomainEvent):
    """Сообщение отправлено."""

    message_id: str = ""
    chat_id: str = ""
    sender_id: str = ""
    message_type: MessageType = MessageType.TEXT


@dataclass(frozen=True)
class MessageUpdated(BaseDomainEvent):
    """Сообщение обновлено."""

    message_id: str = ""


@dataclass(frozen=True)
class MessageDeleted(BaseDomainEvent):
    """Сообщение удалено (soft)."""

    message_id: str = ""


@dataclass(frozen=True)
class MessageReactionAdded(BaseDomainEvent):
    """Реакция на сообщение."""

    message_id: str = ""
    user_id: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class MessageReactionRemoved(BaseDomainEvent):
    """Реакция на сообщение снята."""

    message_id: str = ""
    user_id: str = ""
    emoji: str = ""
