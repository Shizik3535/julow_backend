from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.auth_factor_dto import AuthFactorDTO
from app.context.identity.application.dto.user_auth_status_dto import UserAuthStatusDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class GetUserAuthStatusQuery(BaseQuery):
    """
    Запрос обзора безопасности аккаунта.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class GetUserAuthStatusHandler(BaseQueryHandler[GetUserAuthStatusQuery, UserAuthStatusDTO]):
    """
    Обработчик запроса обзора безопасности.

    Возвращает статус пароля, блокировки, 2FA, OAuth, доверенных устройств.
    """

    def __init__(self, user_auth_repo: UserAuthRepository) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo

    async def handle(self, query: GetUserAuthStatusQuery) -> UserAuthStatusDTO:
        user_id = Id.from_string(query.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(query.user_id)

        auth_factors = [
            AuthFactorDTO(
                method=f.method.value,
                is_enabled=f.is_enabled,
                is_primary=f.is_primary,
                verified_at=f.verified_at,
                priority=f.priority,
            )
            for f in user_auth.auth_factors
        ]

        backup_codes_remaining = sum(
            1 for c in user_auth.backup_codes if not c.is_used
        )

        return UserAuthStatusDTO(
            user_id=str(user_auth.user_id),
            has_password=user_auth.password_hash is not None,
            is_locked=user_auth.is_locked(),
            locked_until=user_auth.locked_until,
            failed_login_attempts=user_auth.failed_login_attempts,
            auth_factors=auth_factors,
            oauth_providers_count=len(user_auth.oauth_links),
            trusted_devices_count=len(user_auth.trusted_devices),
            backup_codes_remaining=backup_codes_remaining,
            created_at=user_auth.created_at,
            updated_at=user_auth.updated_at,
        )
