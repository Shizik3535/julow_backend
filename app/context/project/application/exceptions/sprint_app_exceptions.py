from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class SprintCapabilityNotAvailableException(ApplicationException):
    """Спринты недоступны для текущей методологии."""

    def __init__(self, methodology: str = "") -> None:
        msg = "Спринты недоступны для текущей методологии"
        if methodology:
            msg += f" ({methodology})"
        super().__init__(msg)


class EpicCapabilityNotAvailableException(ApplicationException):
    """Эпики недоступны для текущей методологии."""

    def __init__(self, methodology: str = "") -> None:
        msg = "Эпики недоступны для текущей методологии"
        if methodology:
            msg += f" ({methodology})"
        super().__init__(msg)
