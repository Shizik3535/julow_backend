from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ProjectNotFoundException(EntityNotFoundException):
    """Проект не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Project", id=id)


class MilestoneNotFoundException(EntityNotFoundException):
    """Milestone не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Milestone", id=id)


class ProjectSuspendedException(DomainException):
    """Проект приостановлен."""

    def __init__(self) -> None:
        super().__init__("Проект приостановлен")


class ProjectArchivedException(DomainException):
    """Проект архивирован, действие невозможно."""

    def __init__(self) -> None:
        super().__init__("Проект архивирован, действие невозможно")


class CannotChangeMethodologyWithActiveSprintsException(BusinessRuleViolationException):
    """Нельзя сменить методологию с активными спринтами."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoMethodologyChangeWithActiveSprints",
            message="Нельзя сменить методологию с активными спринтами",
        )


class MethodologyCapabilityNotAvailableException(BusinessRuleViolationException):
    """Функция не доступна для текущей методологии."""

    def __init__(self, capability: str = "") -> None:
        super().__init__(
            rule="MethodologyCapability",
            message=f"Функция не доступна для текущей методологии{f': {capability}' if capability else ''}",
        )


class ProjectPendingDeletionException(DomainException):
    """Проект ожидает удаления."""

    def __init__(self) -> None:
        super().__init__("Проект ожидает удаления")


class CannotTransferOwnershipException(BusinessRuleViolationException):
    """Нельзя передать владение проектом."""

    def __init__(self, reason: str = "") -> None:
        msg = "Нельзя передать владение проектом"
        if reason:
            msg += f": {reason}"
        super().__init__(
            rule="OwnershipTransfer",
            message=msg,
        )
