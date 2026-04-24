"""Unit-тесты для PasswordHash."""

import pytest

from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.shared.domain.exceptions import ValidationException
from tests.factories import PasswordHashFactory


@pytest.mark.unit
class TestPasswordHash:
    def test_valid_hash(self) -> None:
        ph = PasswordHash("$2b$12$somehashvalue")
        assert ph.value == "$2b$12$somehashvalue"

    def test_empty_hash_raises(self) -> None:
        with pytest.raises(ValidationException):
            PasswordHash("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationException):
            PasswordHash("   ")

    def test_str_representation(self) -> None:
        ph = PasswordHash("hashed_value")
        assert str(ph) == "hashed_value"

    def test_equality(self) -> None:
        assert PasswordHash("abc") == PasswordHash("abc")

    def test_factory_creates_valid(self) -> None:
        ph = PasswordHashFactory()
        assert ph.value.startswith("$2b$12$")
