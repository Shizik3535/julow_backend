from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.entities.workspace_member import WorkspaceMember
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.infrastructure.persistence.mappers.workspace_membership_mapper import WorkspaceMembershipMapper
from app.context.workspace.infrastructure.persistence.orm_models.workspace_membership_orm import (
    WorkspaceMemberORM,
    WorkspaceMembershipORM,
)


class SqlWorkspaceMembershipRepository(
    SqlAlchemyRepository[WorkspaceMembership, WorkspaceMembershipORM],
    WorkspaceMembershipRepository,
):
    """SQLAlchemy-реализация WorkspaceMembershipRepository."""

    def __init__(self, session: AsyncSession, mapper: WorkspaceMembershipMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=WorkspaceMembershipORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_workspace_id(self, workspace_id: Id) -> WorkspaceMembership | None:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(WorkspaceMembershipORM).where(WorkspaceMembershipORM.workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_member_by_workspace_and_user(self, workspace_id: Id, user_id: Id) -> WorkspaceMember | None:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(WorkspaceMemberORM)
            .join(WorkspaceMembershipORM, WorkspaceMemberORM.membership_id == WorkspaceMembershipORM.id)
            .where(WorkspaceMembershipORM.workspace_id == ws_uuid, WorkspaceMemberORM.user_id == user_uuid)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._mapper._member_to_domain(orm)

    async def get_members_by_workspace(self, workspace_id: Id) -> list[WorkspaceMember]:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(WorkspaceMemberORM)
            .join(WorkspaceMembershipORM, WorkspaceMemberORM.membership_id == WorkspaceMembershipORM.id)
            .where(WorkspaceMembershipORM.workspace_id == ws_uuid)
        )
        result = await self._session.execute(stmt)
        return [self._mapper._member_to_domain(orm) for orm in result.scalars().all()]

    # ------------------------------------------------------------------
    # Override update для синхронизации дочерних WorkspaceMember
    # ------------------------------------------------------------------

    async def update(self, aggregate: WorkspaceMembership) -> WorkspaceMembership:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(WorkspaceMembershipORM).where(WorkspaceMembershipORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="WorkspaceMembership", id=aggregate.id)

        # Обновить скалярные поля
        orm_model.workspace_id = self._mapper._map_uuid(aggregate.workspace_id)
        orm_model.updated_at = aggregate.updated_at

        # Синхронизация дочерних: diff по id → update / delete / insert
        existing_by_id: dict[uuid.UUID, WorkspaceMemberORM] = {
            m.id: m for m in list(orm_model.members)
        }
        desired_ids = {self._mapper._map_uuid(m.id) for m in aggregate.members}

        # Удаление убранных участников через delete-orphan cascade
        for orm_member in list(orm_model.members):
            if orm_member.id not in desired_ids:
                orm_model.members.remove(orm_member)

        # Обновление существующих + вставка новых
        for member in aggregate.members:
            member_uuid = self._mapper._map_uuid(member.id)
            if member_uuid in existing_by_id:
                orm_member = existing_by_id[member_uuid]
                orm_member.user_id = self._mapper._map_uuid(member.user_id)
                orm_member.display_name = member.display_name
                orm_member.role_id = self._mapper._map_uuid(member.role_id)
                orm_member.joined_at = member.joined_at
                orm_member.is_active = member.is_active
                orm_member.source = member.source.value
                orm_member.invited_by = (
                    self._mapper._map_uuid(member.invited_by)
                    if member.invited_by
                    else None
                )
            else:
                member_orm = self._mapper._member_to_orm(member, aggregate.id)
                member_orm.membership_id = uuid_val
                orm_model.members.append(member_orm)

        await self._session.flush()
        return aggregate
