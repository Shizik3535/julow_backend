from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.team import Team
from app.context.organization.infrastructure.persistence.orm_models.team_orm import TeamORM


class TeamMapper(BaseMapper[Team, TeamORM]):
    """Data Mapper: Team ↔ TeamORM.

    member_ids маппятся отдельно в репозитории через association table.
    """

    def to_domain(self, orm_model: TeamORM) -> Team:
        return Team(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            name=orm_model.name,
            description=orm_model.description,
            lead_id=self._map_id(orm_model.lead_id) if orm_model.lead_id else None,
            member_ids=[],  # заполняется в repo через association table
            icon=orm_model.icon if orm_model.icon else None,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Team) -> TeamORM:
        return TeamORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            name=aggregate.name,
            description=aggregate.description,
            lead_id=self._map_uuid(aggregate.lead_id) if aggregate.lead_id else None,
            icon=aggregate.icon,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
