from app.core.config.auth_settings import AuthSettings
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.infrastructure.auth.argon2_password_adapter import Argon2PasswordAdapter
from app.shared.infrastructure.auth.jwt_auth_adapter import JwtAuthAdapter


def create_auth_token_adapter(settings: AuthSettings) -> AuthTokenPort:
    """Создать JwtAuthAdapter с настройками авторизации."""
    return JwtAuthAdapter(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def create_password_adapter() -> PasswordPort:
    """Создать Argon2PasswordAdapter."""
    return Argon2PasswordAdapter()
