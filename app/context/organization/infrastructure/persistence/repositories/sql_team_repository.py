from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.domain.repositories.team_repository import TeamRepository
from app.context.organization.infrastructure.persistence.mappers.team_mapper import TeamMapper
from app.context.organization.infrastructure.persistence.orm_models.team_orm import (
    TeamORM,
    team_members_table,
)


class SqlTeamRepository(SqlAlchemyRepository[Team, TeamORM], TeamRepository):
    """SQLAlchemy-реализация TeamRepository."""

    def __init__(self, session: AsyncSession, mapper: TeamMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=TeamORM)

    # ------------------------------------------------------------------
    # Загрузка / синхронизация member_ids
    # ------------------------------------------------------------------

    async def _load_member_ids(self, team_uuid) -> list[Id]:
        stmt = select(team_members_table.c.user_id).where(
            team_members_table.c.team_id == team_uuid,
        )
        result = await self._session.execute(stmt)
        return [self._mapper._map_id(row[0]) for row in result.fetchall()]

    async def _enrich_with_members(self, team: Team, team_uuid) -> Team:
        team.member_ids = await self._load_member_ids(team_uuid)
        return team

    async def _sync_members(self, team_uuid, member_ids: list[Id]) -> None:
        await self._session.execute(
            team_members_table.delete().where(team_members_table.c.team_id == team_uuid)
        )
        for mid in member_ids:
            await self._session.execute(
                team_members_table.insert().values(
                    team_id=team_uuid,
                    user_id=self._mapper._map_uuid(mid),
                )
            )

    # ------------------------------------------------------------------
    # Override CRUD
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> Team | None:
        team = await super().get_by_id(id)
        if team is None:
            return None
        return await self._enrich_with_members(team, self._mapper._map_uuid(id))

    async def add(self, aggregate: Team) -> Team:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()
        await self._sync_members(orm_model.id, aggregate.member_ids)
        await self._session.flush()
        return aggregate

    async def update(self, aggregate: Team) -> Team:
        result = await super().update(aggregate)
        uuid_val = self._mapper._map_uuid(aggregate.id)
        await self._sync_members(uuid_val, aggregate.member_ids)
        await self._session.flush()
        return result

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_org(self, org_id: Id) -> list[Team]:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(TeamORM).where(TeamORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        teams = []
        for orm in result.scalars().all():
            team = self._mapper.to_domain(orm)
            team = await self._enrich_with_members(team, orm.id)
            teams.append(team)
        return teams

    async def get_by_member(self, user_id: Id) -> list[Team]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(TeamORM)
            .join(team_members_table, TeamORM.id == team_members_table.c.team_id)
            .where(team_members_table.c.user_id == uuid_val)
        )
        result = await self._session.execute(stmt)
        teams = []
        for orm in result.scalars().all():
            team = self._mapper.to_domain(orm)
            team = await self._enrich_with_members(team, orm.id)
            teams.append(team)
        return teams

    async def get_by_lead(self, user_id: Id) -> list[Team]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(TeamORM).where(TeamORM.lead_id == uuid_val)
        result = await self._session.execute(stmt)
        teams = []
        for orm in result.scalars().all():
            team = self._mapper.to_domain(orm)
            team = await self._enrich_with_members(team, orm.id)
            teams.append(team)
        return teams
