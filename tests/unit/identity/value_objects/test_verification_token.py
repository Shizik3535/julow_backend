"""Unit-тесты для VerificationToken."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from tests.factories import VerificationTokenFactory


@pytest.mark.unit
class TestVerificationToken:
    def test_valid_token(self) -> None:
        token = VerificationToken(value="a" * 32)
        assert token.value == "a" * 32

    def test_short_token_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            VerificationToken(value="short")
        assert exc_info.value.field == "verification_token"

    def test_empty_token_raises(self) -> None:
        with pytest.raises(ValidationException):
            VerificationToken(value="")

    def test_str_representation(self) -> None:
        token = VerificationToken(value="a" * 32)
        assert str(token) == "a" * 32

    def test_factory_creates_valid_token(self) -> None:
        token = VerificationTokenFactory()
        assert len(token.value) >= 16
