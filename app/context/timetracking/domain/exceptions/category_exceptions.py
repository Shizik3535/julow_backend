from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ActivityCategoryNotFoundException(EntityNotFoundException):
    """Категория деятельности не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ActivityCategory", id=id)


class CannotDeleteSystemCategoryException(BusinessRuleViolationException):
    """Нельзя удалить системную категорию."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="SystemCategoryCannotBeDeleted",
            message=f"Нельзя удалить системную категорию{f': {name}' if name else ''}",
        )


class CannotUpdateSystemCategoryException(BusinessRuleViolationException):
    """Нельзя редактировать системную категорию."""

    def __init__(self) -> None:
        super().__init__(
            rule="SystemCategoryCannotBeUpdated",
            message="Нельзя редактировать системную категорию",
        )


class ActivityCategoryInUseException(BusinessRuleViolationException):
    """Категория используется в записях."""

    def __init__(self) -> None:
        super().__init__(
            rule="CategoryInUse",
            message="Категория используется в записях",
        )


class DuplicateActivityCategoryException(BusinessRuleViolationException):
    """Категория с таким именем уже существует в workspace."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="UniqueActivityCategory",
            message=f"Категория с таким именем уже существует{f': {name}' if name else ''}",
        )


class DuplicateTimeEntryTagException(BusinessRuleViolationException):
    """Тег с таким именем уже существует."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="UniqueTimeEntryTag",
            message=f"Тег с таким именем уже существует{f': {name}' if name else ''}",
        )
