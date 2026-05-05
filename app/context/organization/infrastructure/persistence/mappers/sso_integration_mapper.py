from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.infrastructure.persistence.orm_models.sso_integration_orm import (
    SSOIntegrationORM,
)


class SSOIntegrationMapper(BaseMapper[SSOIntegration, SSOIntegrationORM]):
    """Data Mapper: SSOIntegration ↔ SSOIntegrationORM."""

    def to_domain(self, orm_model: SSOIntegrationORM) -> SSOIntegration:
        return SSOIntegration(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            provider=SSOProvider(orm_model.provider),
            entity_id=orm_model.entity_id,
            sso_url=orm_model.sso_url,
            certificate=orm_model.certificate,
            is_active=orm_model.is_active,
            group_mapping=orm_model.group_mapping,
            attribute_mapping=orm_model.attribute_mapping,
            email_domains=orm_model.email_domains or [],
            auto_provision=orm_model.auto_provision,
            default_role_id=self._map_id(orm_model.default_role_id) if orm_model.default_role_id else None,
            added_at=orm_model.added_at,
            added_by=self._map_id(orm_model.added_by),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: SSOIntegration) -> SSOIntegrationORM:
        return SSOIntegrationORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            provider=aggregate.provider.value,
            entity_id=aggregate.entity_id,
            sso_url=aggregate.sso_url,
            certificate=aggregate.certificate,
            is_active=aggregate.is_active,
            group_mapping=aggregate.group_mapping,
            attribute_mapping=aggregate.attribute_mapping,
            email_domains=aggregate.email_domains if aggregate.email_domains else None,
            auto_provision=aggregate.auto_provision,
            default_role_id=self._map_uuid(aggregate.default_role_id) if aggregate.default_role_id else None,
            added_at=aggregate.added_at,
            added_by=self._map_uuid(aggregate.added_by),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
