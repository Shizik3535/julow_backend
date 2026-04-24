"""Unit-тесты для исключений Profile BC."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException, ValidationException
from app.context.profile.domain.exceptions.profile_exceptions import (
    DuplicatePinnedItemException,
    DuplicateSocialLinkException,
    InvalidDateFormatException,
    InvalidHotkeyException,
    InvalidStartPageException,
    ProfileNotFoundException,
)


@pytest.mark.unit
class TestProfileNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = ProfileNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "UserProfile"

    def test_is_domain(self) -> None:
        exc = ProfileNotFoundException(id="x")
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestInvalidHotkeyException:
    def test_is_validation(self) -> None:
        exc = InvalidHotkeyException()
        assert isinstance(exc, ValidationException)
        assert exc.field == "hotkey"

    def test_with_detail(self) -> None:
        exc = InvalidHotkeyException(detail="unknown action")
        assert "unknown action" in exc.message


@pytest.mark.unit
class TestInvalidDateFormatException:
    def test_is_validation(self) -> None:
        exc = InvalidDateFormatException("YYYY")
        assert isinstance(exc, ValidationException)
        assert exc.field == "date_format"

    def test_stores_value(self) -> None:
        exc = InvalidDateFormatException("YYYY")
        assert exc.value == "YYYY"


@pytest.mark.unit
class TestInvalidStartPageException:
    def test_is_validation(self) -> None:
        exc = InvalidStartPageException("")
        assert isinstance(exc, ValidationException)
        assert exc.field == "start_page"


@pytest.mark.unit
class TestDuplicatePinnedItemException:
    def test_is_business_rule(self) -> None:
        exc = DuplicatePinnedItemException(target_type="task", target_id="123")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_stores_target_info(self) -> None:
        exc = DuplicatePinnedItemException(target_type="task", target_id="123")
        assert exc.target_type == "task"
        assert exc.target_id == "123"


@pytest.mark.unit
class TestDuplicateSocialLinkException:
    def test_is_business_rule(self) -> None:
        exc = DuplicateSocialLinkException(platform="github")
        assert isinstance(exc, BusinessRuleViolationException)

    def test_stores_platform(self) -> None:
        exc = DuplicateSocialLinkException(platform="github")
        assert exc.platform == "github"
