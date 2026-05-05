from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.infrastructure.persistence.mappers.sso_integration_mapper import SSOIntegrationMapper
from app.context.organization.infrastructure.persistence.orm_models.sso_integration_orm import SSOIntegrationORM


class SqlSSOIntegrationRepository(SqlAlchemyRepository[SSOIntegration, SSOIntegrationORM], SSOIntegrationRepository):
    """SQLAlchemy-реализация SSOIntegrationRepository."""

    def __init__(self, session: AsyncSession, mapper: SSOIntegrationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=SSOIntegrationORM)

    async def get_by_org_id(self, org_id: Id) -> list[SSOIntegration]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(SSOIntegrationORM).where(SSOIntegrationORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_org_and_provider(self, org_id: Id, provider: SSOProvider) -> SSOIntegration | None:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(SSOIntegrationORM).where(
            SSOIntegrationORM.org_id == uuid_val,
            SSOIntegrationORM.provider == provider.value,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_active_by_email_domain(self, email_domain: str) -> SSOIntegration | None:
        stmt = (
            select(SSOIntegrationORM)
            .where(SSOIntegrationORM.is_active.is_(True))
            .where(text("email_domains @> :domain_json"))
            .params(domain_json=f'["{email_domain}"]')
            .limit(1)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None
