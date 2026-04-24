from __future__ import annotations

from enum import Enum


class TimeEntryStatus(Enum):
    """
    Жизненный цикл записи времени.

    Значения:
        DRAFT: Черновик (можно редактировать)
        SUBMITTED: Отправлено на утверждение
        APPROVED: Утверждено менеджером
        REJECTED: Отклонено (с причиной)
        LOCKED: Заблокировано (период закрыт)
    """

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOCKED = "locked"
