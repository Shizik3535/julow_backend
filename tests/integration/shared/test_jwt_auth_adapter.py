"""Интеграционные тесты JwtAuthAdapter (реальный PyJWT)."""

import uuid

import pytest

from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.infrastructure.auth.jwt_auth_adapter import JwtAuthAdapter


@pytest.mark.integration
class TestJwtAuthAdapter:
    """Тесты генерации и валидации JWT через PyJWT."""

    @pytest.fixture
    def user_id(self) -> str:
        return str(uuid.uuid4())

    # ── generate_access_token ────────────────────────────────────────────

    def test_generate_access_token(self, jwt_adapter: JwtAuthAdapter, user_id: str) -> None:
        result = jwt_adapter.generate_access_token(user_id)
        assert result.access_token
        assert result.access_expires_in > 0

    def test_validate_access_token(self, jwt_adapter: JwtAuthAdapter, user_id: str) -> None:
        token = jwt_adapter.generate_access_token(user_id)
        payload = jwt_adapter.validate_access_token(token.access_token)
        assert str(payload.user_id) == user_id
        assert payload.token_type == "access"

    # ── generate_token_pair ──────────────────────────────────────────────

    def test_generate_token_pair(self, jwt_adapter: JwtAuthAdapter, user_id: str) -> None:
        pair = jwt_adapter.generate_token_pair(user_id)
        assert pair.access_token
        assert pair.refresh_token
        assert pair.access_token != pair.refresh_token
        assert pair.access_expires_in > 0
        assert pair.refresh_expires_in > 0

    def test_validate_refresh_token(self, jwt_adapter: JwtAuthAdapter, user_id: str) -> None:
        pair = jwt_adapter.generate_token_pair(user_id)
        payload = jwt_adapter.validate_refresh_token(pair.refresh_token)
        assert str(payload.user_id) == user_id
        assert payload.token_type == "refresh"

    # ── error cases ──────────────────────────────────────────────────────

    def test_validate_access_token_with_refresh_token_raises(
        self, jwt_adapter: JwtAuthAdapter, user_id: str
    ) -> None:
        pair = jwt_adapter.generate_token_pair(user_id)
        with pytest.raises(InvalidTokenException):
            jwt_adapter.validate_access_token(pair.refresh_token)

    def test_validate_refresh_token_with_access_token_raises(
        self, jwt_adapter: JwtAuthAdapter, user_id: str
    ) -> None:
        pair = jwt_adapter.generate_token_pair(user_id)
        with pytest.raises(InvalidTokenException):
            jwt_adapter.validate_refresh_token(pair.access_token)

    def test_validate_invalid_token_raises(self, jwt_adapter: JwtAuthAdapter) -> None:
        with pytest.raises(InvalidTokenException):
            jwt_adapter.validate_access_token("invalid.jwt.token")

    def test_expired_token_raises(self) -> None:
        adapter = JwtAuthAdapter(
            secret_key="test-secret-key-that-is-at-least-32-bytes-long",
            algorithm="HS256",
            access_token_expire_minutes=0,
            refresh_token_expire_days=0,
        )
        pair = adapter.generate_token_pair(str(uuid.uuid4()))
        with pytest.raises(InvalidTokenException):
            adapter.validate_access_token(pair.access_token)
