"""Unit-тесты для TwoFactorMethod."""

import pytest

from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


@pytest.mark.unit
class TestTwoFactorMethod:
    def test_all_methods_exist(self) -> None:
        assert TwoFactorMethod.TOTP.value == "totp"
        assert TwoFactorMethod.EMAIL_CODE.value == "email_code"
        assert TwoFactorMethod.APP.value == "app"

    def test_methods_are_distinct(self) -> None:
        values = [m.value for m in TwoFactorMethod]
        assert len(values) == len(set(values))
