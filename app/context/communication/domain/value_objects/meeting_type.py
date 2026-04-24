from __future__ import annotations

from enum import Enum


class MeetingType(Enum):
    """
    Формат совещания.

    Новые форматы = значение enum.

    Значения:
        IN_PERSON: Очное
        VIDEO_CALL: Видеозвонок
        PHONE_CALL: Телефонный звонок
        HYBRID: Гибридное
    """

    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"
    PHONE_CALL = "phone_call"
    HYBRID = "hybrid"
