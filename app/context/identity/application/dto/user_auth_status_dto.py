from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.auth_factor_dto import AuthFactorDTO


class UserAuthStatusDTO(BaseDTO):
    """
    DTO обзора безопасности аккаунта (Identity BC).

    Атрибуты:
        user_id: Идентификатор пользователя.
        has_password: Установлен ли пароль.
        is_locked: Заблокирован ли аккаунт.
        locked_until: Время разблокировки.
        failed_login_attempts: Количество неудачных попыток.
        auth_factors: Список факторов 2FA.
        oauth_providers_count: Количество привязанных OAuth-провайдеров.
        trusted_devices_count: Количество доверенных устройств.
        backup_codes_remaining: Оставшиеся резервные коды.
        created_at: Время создания UserAuth.
        updated_at: Время последнего обновления.
    """

    user_id: str
    has_password: bool
    is_locked: bool
    locked_until: datetime | None = None
    failed_login_attempts: int = 0
    auth_factors: list[AuthFactorDTO] = []
    oauth_providers_count: int = 0
    trusted_devices_count: int = 0
    backup_codes_remaining: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
