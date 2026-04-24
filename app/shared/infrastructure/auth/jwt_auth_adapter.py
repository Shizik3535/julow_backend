from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from app.core.logging import get_logger
from app.shared.application.ports.auth.auth_dto import AccessToken, TokenPair, TokenPayload
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.application.ports.auth.auth_port import AuthTokenPort

logger = get_logger(__name__)


class JwtAuthAdapter(AuthTokenPort):
    """
    Реализация AuthTokenPort на основе PyJWT.

    Генерирует и валидирует JWT токены (access + refresh).

    Аргументы конструктора:
        secret_key: Секретный ключ для подписи JWT.
        algorithm: Алгоритм подписи (например, HS256).
        access_token_expire_minutes: Время жизни access-токена в минутах.
        refresh_token_expire_days: Время жизни refresh-токена в днях.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_token_expire_minutes
        self._refresh_expire_days = refresh_token_expire_days

    def generate_access_token(self, user_id: str) -> AccessToken:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._access_expire_minutes)

        payload = {
            "jti": str(uuid4()),
            "user_id": user_id,
            "token_type": "access",
            "exp": expires_at,
            "iat": now,
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        logger.debug(
            "Access token generated",
            user_id=user_id,
            access_expires_in=self._access_expire_minutes * 60,
        )

        return AccessToken(
            access_token=token,
            access_expires_in=self._access_expire_minutes * 60,
        )

    def generate_token_pair(self, user_id: str) -> TokenPair:
        now = datetime.now(timezone.utc)

        access_expires_at = now + timedelta(minutes=self._access_expire_minutes)
        refresh_expires_at = now + timedelta(days=self._refresh_expire_days)

        access_payload = {
            "jti": str(uuid4()),
            "user_id": user_id,
            "token_type": "access",
            "exp": access_expires_at,
            "iat": now,
        }
        refresh_payload = {
            "jti": str(uuid4()),
            "user_id": user_id,
            "token_type": "refresh",
            "exp": refresh_expires_at,
            "iat": now,
        }

        access_token = jwt.encode(access_payload, self._secret_key, algorithm=self._algorithm)
        refresh_token = jwt.encode(refresh_payload, self._secret_key, algorithm=self._algorithm)

        logger.debug(
            "Token pair generated",
            user_id=user_id,
            access_expires_in=self._access_expire_minutes * 60,
            refresh_expires_in=self._refresh_expire_days * 86400,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in=self._access_expire_minutes * 60,
            refresh_expires_in=self._refresh_expire_days * 86400,
        )

    def validate_access_token(self, token: str) -> TokenPayload:
        payload = self._decode_token(token, expected_type="access")
        logger.debug("Access token validated", user_id=payload.user_id)
        return payload

    def validate_refresh_token(self, token: str) -> TokenPayload:
        payload = self._decode_token(token, expected_type="refresh")
        logger.debug("Refresh token validated", user_id=payload.user_id)
        return payload

    def _decode_token(self, token: str, expected_type: str) -> TokenPayload:
        try:
            decoded = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired", token_type=expected_type)
            raise InvalidTokenException(f"Expired {expected_type} token")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", token_type=expected_type, error=str(e))
            raise InvalidTokenException(f"Invalid {expected_type} token")

        token_type = decoded.get("token_type")
        if token_type != expected_type:
            logger.warning("Unexpected token type", expected=expected_type, actual=token_type)
            raise InvalidTokenException(
                f"Expected {expected_type} token, got {token_type}"
            )

        return TokenPayload(
            user_id=UUID(decoded["user_id"]),
            token_type=token_type,
            exp=decoded["exp"],
        )
