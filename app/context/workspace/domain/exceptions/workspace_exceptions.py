from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class WorkspaceNotFoundException(EntityNotFoundException):
    """Workspace не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Workspace", id=id)


class WorkspaceSuspendedException(DomainException):
    """Workspace приостановлен."""

    def __init__(self) -> None:
        super().__init__("Workspace приостановлен")


class WorkspaceArchivedException(DomainException):
    """Workspace архивирован, действие невозможно."""

    def __init__(self) -> None:
        super().__init__("Workspace архивирован, действие невозможно")


class CannotRemoveOwnerException(BusinessRuleViolationException):
    """Нельзя удалить владельца."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(
            rule="OwnerCannotBeRemoved",
            message=f"Нельзя удалить владельца{f': {user_id}' if user_id else ''}",
        )


class CannotRemoveLastOwnerException(BusinessRuleViolationException):
    """Нельзя удалить последнего владельца."""

    def __init__(self) -> None:
        super().__init__(
            rule="AtLeastOneOwner",
            message="Нельзя удалить последнего владельца workspace",
        )


class CannotTransferOwnershipException(BusinessRuleViolationException):
    """Нельзя передать владение."""

    def __init__(self, reason: str = "") -> None:
        msg = "Нельзя передать владение"
        if reason:
            msg += f": {reason}"
        super().__init__(
            rule="OwnershipTransfer",
            message=msg,
        )


class SecurityPolicyViolationException(DomainException):
    """Нарушение политики безопасности."""

    def __init__(self, detail: str = "") -> None:
        msg = "Нарушение политики безопасности"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class IPAllowlistViolationException(DomainException):
    """IP не в allowlist."""

    def __init__(self, ip: str = "") -> None:
        msg = "IP не в allowlist"
        if ip:
            msg += f": {ip}"
        super().__init__(msg)


class SSORequiredException(DomainException):
    """Требуется SSO аутентификация."""

    def __init__(self) -> None:
        super().__init__("Требуется SSO аутентификация")


class CircularWorkspaceHierarchyException(BusinessRuleViolationException):
    """Циклическая ссылка в иерархии workspace."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoCircularWorkspaceReference",
            message="Циклическая ссылка в иерархии workspace",
        )


class ParentWorkspaceNotFoundException(EntityNotFoundException):
    """Родительский workspace не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Workspace", id=id)


class CannotArchiveWithChildrenException(BusinessRuleViolationException):
    """Нельзя архивировать workspace с активными дочерними."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoArchiveWithChildren",
            message="Нельзя архивировать workspace с активными дочерними",
        )


class WorkspaceLimitExceededException(BusinessRuleViolationException):
    """Лимит workspace превышен."""

    def __init__(self, limit_name: str = "") -> None:
        super().__init__(
            rule="WorkspaceLimit",
            message=f"Лимит workspace превышен{f': {limit_name}' if limit_name else ''}",
        )


class WorkspaceAlreadyArchivedException(BusinessRuleViolationException):
    """Workspace уже архивирован."""

    def __init__(self) -> None:
        super().__init__(
            rule="WorkspaceAlreadyArchived",
            message="Workspace уже архивирован",
        )


class WorkspaceNotArchivedException(BusinessRuleViolationException):
    """Workspace не в архиве."""

    def __init__(self) -> None:
        super().__init__(
            rule="WorkspaceNotArchived",
            message="Workspace не в архиве",
        )


class WorkspaceAlreadySuspendedException(BusinessRuleViolationException):
    """Workspace уже приостановлен."""

    def __init__(self) -> None:
        super().__init__(
            rule="WorkspaceAlreadySuspended",
            message="Workspace уже приостановлен",
        )


class WorkspaceNotSuspendedException(BusinessRuleViolationException):
    """Workspace не приостановлен."""

    def __init__(self) -> None:
        super().__init__(
            rule="WorkspaceNotSuspended",
            message="Workspace не приостановлен",
        )


class WorkspaceDeletionAlreadyRequestedException(BusinessRuleViolationException):
    """Запрос на удаление workspace уже отправлен."""

    def __init__(self) -> None:
        super().__init__(
            rule="WorkspaceDeletionAlreadyRequested",
            message="Запрос на удаление workspace уже отправлен",
        )
