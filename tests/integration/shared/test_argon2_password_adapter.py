"""Интеграционные тесты Argon2PasswordAdapter (реальный argon2)."""

import pytest

from app.shared.infrastructure.auth.argon2_password_adapter import Argon2PasswordAdapter


@pytest.mark.integration
class TestArgon2PasswordAdapter:
    """Тесты хеширования и верификации паролей через argon2."""

    def test_hash_password_returns_string(self, password_adapter: Argon2PasswordAdapter) -> None:
        hashed = password_adapter.hash_password("my-secret-password")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_produces_different_hashes(self, password_adapter: Argon2PasswordAdapter) -> None:
        h1 = password_adapter.hash_password("same-password")
        h2 = password_adapter.hash_password("same-password")
        assert h1 != h2  # разные соли

    def test_verify_password_correct(self, password_adapter: Argon2PasswordAdapter) -> None:
        password = "correct-horse-battery-staple"
        hashed = password_adapter.hash_password(password)
        assert password_adapter.verify_password(password, hashed) is True

    def test_verify_password_wrong(self, password_adapter: Argon2PasswordAdapter) -> None:
        hashed = password_adapter.hash_password("right-password")
        assert password_adapter.verify_password("wrong-password", hashed) is False

    def test_hash_contains_argon2_prefix(self, password_adapter: Argon2PasswordAdapter) -> None:
        hashed = password_adapter.hash_password("test123")
        assert hashed.startswith("$argon2")
