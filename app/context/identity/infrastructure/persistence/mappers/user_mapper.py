from __future__ import annotations

from app.shared.domain.value_objects.email_vo import Email
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.value_objects.account_status import AccountStatus
from app.context.identity.infrastructure.persistence.orm_models.user_orm import UserORM


class UserMapper(BaseMapper[User, UserORM]):
    """Data Mapper: User ↔ UserORM."""

    def to_domain(self, orm_model: UserORM) -> User:
        return User(
            id=self._map_id(orm_model.id),
            email=Email(orm_model.email),
            status=AccountStatus(orm_model.status),
            role_ids=[self._map_id(r.id) for r in orm_model.roles or []],
            is_email_confirmed=orm_model.is_email_confirmed,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: User) -> UserORM:
        return UserORM(
            id=self._map_uuid(aggregate.id),
            email=aggregate.email.value,
            status=aggregate.status.value,
            is_email_confirmed=aggregate.is_email_confirmed,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
