"""Unit-тесты для RefreshToken."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from tests.factories import RefreshTokenFactory


@pytest.mark.unit
class TestRefreshToken:
    def test_valid_token(self) -> None:
        rt = RefreshToken(value="some_refresh_token")
        assert rt.value == "some_refresh_token"

    def test_empty_token_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            RefreshToken(value="")
        assert exc_info.value.field == "refresh_token"

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationException):
            RefreshToken(value="   ")

    def test_str_representation(self) -> None:
        rt = RefreshToken(value="token123")
        assert str(rt) == "token123"

    def test_factory_creates_valid_token(self) -> None:
        rt = RefreshTokenFactory()
        assert len(rt.value) > 0
