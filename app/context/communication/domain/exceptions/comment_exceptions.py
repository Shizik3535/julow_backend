from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class CommentNotFoundException(EntityNotFoundException):
    """Комментарий не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Comment", id=id)


class CommentDeletedException(DomainException):
    """Комментарий удалён."""

    def __init__(self) -> None:
        super().__init__("Комментарий удалён")


class CannotDeleteCommentException(BusinessRuleViolationException):
    """Нельзя удалить комментарий (системный)."""

    def __init__(self) -> None:
        super().__init__(
            rule="CannotDeleteSystemComment",
            message="Нельзя удалить системный комментарий",
        )


class CannotUpdateCommentException(BusinessRuleViolationException):
    """Нельзя редактировать комментарий (системный/удалённый)."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            rule="CannotUpdateComment",
            message=f"Нельзя редактировать комментарий{f': {reason}' if reason else ''}",
        )


class DuplicateReactionException(BusinessRuleViolationException):
    """Реакция уже поставлена."""

    def __init__(self) -> None:
        super().__init__(
            rule="UniqueReaction",
            message="Реакция уже поставлена (same user_id + emoji)",
        )
