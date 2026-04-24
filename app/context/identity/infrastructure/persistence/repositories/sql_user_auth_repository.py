from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.infrastructure.persistence.mappers.user_auth_mapper import UserAuthMapper
from app.context.identity.infrastructure.persistence.orm_models.user_auth_orm import (
    OAuthLinkORM,
    UserAuthORM,
)


class SqlUserAuthRepository(SqlAlchemyRepository[UserAuth, UserAuthORM], UserAuthRepository):
    """SQLAlchemy-реализация UserAuthRepository."""

    def __init__(self, session: AsyncSession, mapper: UserAuthMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=UserAuthORM)

    async def get_by_user_id(self, user_id: Id) -> UserAuth | None:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(UserAuthORM).where(UserAuthORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_email(self, email: Email) -> UserAuth | None:
        stmt = select(UserAuthORM).where(UserAuthORM.email == email.value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_oauth_provider(
        self,
        provider: AuthProvider,
        provider_user_id: str,
    ) -> UserAuth | None:
        stmt = (
            select(UserAuthORM)
            .join(OAuthLinkORM, UserAuthORM.id == OAuthLinkORM.user_auth_id)
            .where(
                OAuthLinkORM.provider == provider.value,
                OAuthLinkORM.provider_user_id == provider_user_id,
            )
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def update(self, aggregate: UserAuth) -> UserAuth:
        """Обновляет UserAuth с полной синхронизацией дочерних коллекций."""
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(UserAuthORM).where(UserAuthORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="UserAuth", id=aggregate.id)

        # Обновить скалярные поля напрямую из агрегата
        orm_model.user_id = self._mapper._map_uuid(aggregate.user_id)
        orm_model.email = aggregate.email.value
        orm_model.password_hash = aggregate.password_hash.value if aggregate.password_hash else None
        orm_model.failed_login_attempts = aggregate.failed_login_attempts
        orm_model.locked_until = aggregate.locked_until
        orm_model.updated_at = aggregate.updated_at

        # Синхронизация дочерних коллекций: создаём дочерние ORM напрямую
        # (без промежуточного parent ORM), чтобы избежать каскадного INSERT родителя.
        # cascade="all, delete-orphan" обеспечит удаление старых и вставку новых.
        orm_model.auth_factors = [
            self._mapper._factor_to_orm(f, uuid_val) for f in aggregate.auth_factors
        ]
        orm_model.oauth_links = [
            self._mapper._oauth_to_orm(o, uuid_val) for o in aggregate.oauth_links
        ]
        orm_model.login_attempts = [
            self._mapper._attempt_to_orm(a, uuid_val) for a in aggregate.login_attempts
        ]
        orm_model.trusted_devices = [
            self._mapper._device_to_orm(d, uuid_val) for d in aggregate.trusted_devices
        ]
        orm_model.email_verifications = [
            self._mapper._verification_to_orm(v, uuid_val) for v in aggregate.verifications
        ]
        orm_model.backup_codes = [
            self._mapper._backup_to_orm(b, uuid_val) for b in aggregate.backup_codes
        ]

        await self._session.flush()
        return aggregate
