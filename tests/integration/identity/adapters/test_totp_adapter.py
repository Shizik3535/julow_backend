"""Интеграционные тесты PyOTPTotpAdapter (реальный pyotp)."""

import pyotp
import pytest

from app.context.identity.infrastructure.two_fa.totp_adapter import PyOTPTotpAdapter


@pytest.mark.integration
class TestPyOTPTotpAdapter:
    """Тесты TOTP через реальный pyotp."""

    @pytest.fixture
    def adapter(self) -> PyOTPTotpAdapter:
        return PyOTPTotpAdapter()

    def test_generate_secret(self, adapter: PyOTPTotpAdapter) -> None:
        secret = adapter.generate_secret()
        assert isinstance(secret, str)
        assert len(secret) > 0

    def test_generate_secret_unique(self, adapter: PyOTPTotpAdapter) -> None:
        s1 = adapter.generate_secret()
        s2 = adapter.generate_secret()
        assert s1 != s2

    def test_verify_code_valid(self, adapter: PyOTPTotpAdapter) -> None:
        secret = adapter.generate_secret()
        # Генерируем реальный TOTP-код для текущего момента
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert adapter.verify_code(secret, code) is True

    def test_verify_code_invalid(self, adapter: PyOTPTotpAdapter) -> None:
        secret = adapter.generate_secret()
        assert adapter.verify_code(secret, "000000") is False

    def test_get_provisioning_uri(self, adapter: PyOTPTotpAdapter) -> None:
        secret = adapter.generate_secret()
        uri = adapter.get_provisioning_uri(secret, "user@example.com", "Julow")
        assert uri.startswith("otpauth://totp/")
        assert "user@example.com" in uri or "user%40example.com" in uri
        assert "Julow" in uri
