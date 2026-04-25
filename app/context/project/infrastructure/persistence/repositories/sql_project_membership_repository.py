from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.entities.project_member import ProjectMember
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.infrastructure.persistence.mappers.project_membership_mapper import ProjectMembershipMapper
from app.context.project.infrastructure.persistence.orm_models.project_membership_orm import (
    ProjectMemberORM,
    ProjectMembershipORM,
)


class SqlProjectMembershipRepository(
    SqlAlchemyRepository[ProjectMembership, ProjectMembershipORM],
    ProjectMembershipRepository,
):
    """SQLAlchemy-реализация ProjectMembershipRepository."""

    def __init__(self, session: AsyncSession, mapper: ProjectMembershipMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ProjectMembershipORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_project_id(self, project_id: Id) -> ProjectMembership | None:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(ProjectMembershipORM).where(ProjectMembershipORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_member_by_project_and_user(self, project_id: Id, user_id: Id) -> ProjectMember | None:
        proj_uuid = self._mapper._map_uuid(project_id)
        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(ProjectMemberORM)
            .join(ProjectMembershipORM, ProjectMemberORM.membership_id == ProjectMembershipORM.id)
            .where(ProjectMembershipORM.project_id == proj_uuid, ProjectMemberORM.user_id == user_uuid)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._mapper._member_orm_to_domain(orm)

    async def get_members_by_project(self, project_id: Id) -> list[ProjectMember]:
        proj_uuid = self._mapper._map_uuid(project_id)
        stmt = (
            select(ProjectMemberORM)
            .join(ProjectMembershipORM, ProjectMemberORM.membership_id == ProjectMembershipORM.id)
            .where(ProjectMembershipORM.project_id == proj_uuid)
        )
        result = await self._session.execute(stmt)
        return [self._mapper._member_orm_to_domain(orm) for orm in result.scalars().all()]

    # ------------------------------------------------------------------
    # Override update — синхронизация дочерних ProjectMember
    # ------------------------------------------------------------------

    async def update(self, aggregate: ProjectMembership) -> ProjectMembership:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(ProjectMembershipORM).where(ProjectMembershipORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="ProjectMembership", id=aggregate.id)

        # Скалярные поля
        orm_model.project_id = self._mapper._map_uuid(aggregate.project_id)

        # Синхронизация дочерних: diff по id
        existing_by_id: dict[uuid.UUID, ProjectMemberORM] = {
            m.id: m for m in list(orm_model.members)
        }
        desired_ids = {self._mapper._map_uuid(m.id) for m in aggregate.members}

        # Удаление убранных
        for orm_member in list(orm_model.members):
            if orm_member.id not in desired_ids:
                orm_model.members.remove(orm_member)

        # Обновление существующих + вставка новых
        for member in aggregate.members:
            member_uuid = self._mapper._map_uuid(member.id)
            if member_uuid in existing_by_id:
                orm_member = existing_by_id[member_uuid]
                orm_member.user_id = self._mapper._map_uuid(member.user_id)
                orm_member.role_id = self._mapper._map_uuid(member.role_id)
                orm_member.joined_at = member.joined_at
                orm_member.is_active = member.is_active
            else:
                member_orm = self._mapper._member_to_orm(member, aggregate.id)
                member_orm.membership_id = uuid_val
                orm_model.members.append(member_orm)

        await self._session.flush()
        return aggregate
