from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class TaskTemplateNotFoundException(EntityNotFoundException):
    """Шаблон задачи не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="TaskTemplate", id=id)


class CannotDeleteSystemTemplateException(BusinessRuleViolationException):
    """Нельзя удалить системный шаблон."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="SystemTemplateCannotBeDeleted",
            message=f"Нельзя удалить системный шаблон{f': {name}' if name else ''}",
        )
