from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.context.identity.presentation.schemas.responses.auth_factor_response import AuthFactorResponse


class UserAuthStatusResponse(BaseModel):
    """
    Ответ с обзором безопасности аккаунта.

    Содержит информацию о пароле, блокировке, 2FA-факторах,
    OAuth-провайдерах, доверенных устройствах и резервных кодах.

    Атрибуты:
        user_id: UUID пользователя.
        has_password: Установлен ли пароль.
        is_locked: Заблокирован ли аккаунт.
        locked_until: Время разблокировки (UTC).
        failed_login_attempts: Количество неудачных попыток входа.
        auth_factors: Список факторов 2FA.
        oauth_providers_count: Количество привязанных OAuth-провайдеров.
        trusted_devices_count: Количество доверенных устройств.
        backup_codes_remaining: Оставшиеся резервные коды.
        created_at: Время создания записи аутентификации (UTC).
        updated_at: Время последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID пользователя", examples=["550e8400-e29b-41d4-a716-446655440000"])
    has_password: bool = Field(..., description="Установлен ли пароль")
    is_locked: bool = Field(..., description="Заблокирован ли аккаунт")
    locked_until: datetime | None = Field(default=None, description="Время разблокировки (UTC)")
    failed_login_attempts: int = Field(default=0, description="Количество неудачных попыток входа", examples=[0])
    auth_factors: list[AuthFactorResponse] = Field(default_factory=list, description="Список факторов 2FA")
    oauth_providers_count: int = Field(default=0, description="Количество привязанных OAuth-провайдеров", examples=[2])
    trusted_devices_count: int = Field(default=0, description="Количество доверенных устройств", examples=[1])
    backup_codes_remaining: int = Field(default=0, description="Оставшиеся резервные коды", examples=[8])
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
    updated_at: datetime | None = Field(default=None, description="Время последнего обновления (UTC)")
