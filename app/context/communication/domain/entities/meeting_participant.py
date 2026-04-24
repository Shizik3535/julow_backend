from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.value_objects.rsvp_status import RSVPStatus


@dataclass
class MeetingParticipant(BaseEntity):
    """
    Сущность участника совещания.

    Принадлежит агрегату Meeting.

    Атрибуты:
        user_id: ID пользователя.
        is_mandatory: Обязательное участие.
        joined_at: Время присоединения.
        rsvp_status: Статус ответа на приглашение.
    """

    user_id: Id = field(default_factory=Id.generate)
    is_mandatory: bool = True
    joined_at: datetime | None = None
    rsvp_status: RSVPStatus = RSVPStatus.PENDING
