from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class CustomFieldDefinitionNotFoundException(EntityNotFoundException):
    """Определение кастомного поля не найдено."""

    def __init__(self, name: str = "") -> None:
        super().__init__(entity_type="CustomFieldDefinition", id=name)


class DuplicateCustomFieldException(BusinessRuleViolationException):
    """Кастомное поле с таким именем уже существует."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="UniqueCustomFieldName",
            message=f"Кастомное поле с таким именем уже существует{f': {name}' if name else ''}",
        )
