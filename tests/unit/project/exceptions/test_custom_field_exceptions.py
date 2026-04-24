"""Unit-тесты для исключений CustomField (Project BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.project.domain.exceptions.custom_field_exceptions import (
    CustomFieldDefinitionNotFoundException,
    DuplicateCustomFieldException,
)


@pytest.mark.unit
class TestCustomFieldDefinitionNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = CustomFieldDefinitionNotFoundException(name="priority")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "CustomFieldDefinition"

    def test_message_contains_name(self) -> None:
        exc = CustomFieldDefinitionNotFoundException(name="priority")
        assert "priority" in exc.message


@pytest.mark.unit
class TestDuplicateCustomFieldException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateCustomFieldException()
        assert isinstance(exc, BusinessRuleViolationException)

    def test_rule(self) -> None:
        exc = DuplicateCustomFieldException()
        assert exc.rule == "UniqueCustomFieldName"

    def test_message_with_name(self) -> None:
        exc = DuplicateCustomFieldException(name="priority")
        assert "priority" in exc.message
