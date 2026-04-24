"""Unit-тесты для исключений TaskTemplate aggregate (Task BC)."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.context.task.domain.exceptions.task_template_exceptions import (
    TaskTemplateNotFoundException,
    CannotDeleteSystemTemplateException,
)


@pytest.mark.unit
class TestTaskTemplateNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = TaskTemplateNotFoundException(id="tpl-1")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "TaskTemplate"

    def test_message_contains_id(self) -> None:
        exc = TaskTemplateNotFoundException(id="tpl-1")
        assert "tpl-1" in exc.message


@pytest.mark.unit
class TestCannotDeleteSystemTemplateException:
    def test_is_business_rule(self) -> None:
        exc = CannotDeleteSystemTemplateException()
        assert isinstance(exc, BusinessRuleViolationException)
        assert exc.rule == "SystemTemplateCannotBeDeleted"

    def test_message_contains_name(self) -> None:
        exc = CannotDeleteSystemTemplateException(name="Bug Report")
        assert "Bug Report" in exc.message
