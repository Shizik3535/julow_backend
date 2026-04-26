from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class MilestoneCapabilityNotAvailableException(ApplicationException):
    """Milestones недоступны для текущей методологии."""

    def __init__(self, methodology: str = "") -> None:
        msg = "Milestones недоступны для текущей методологии"
        if methodology:
            msg += f" ({methodology})"
        super().__init__(msg)
