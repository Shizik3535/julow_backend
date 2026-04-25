from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository
from app.context.project.infrastructure.persistence.mappers.retro_template_mapper import RetroTemplateMapper
from app.context.project.infrastructure.persistence.orm_models.retro_template_orm import RetroTemplateORM


class SqlRetroTemplateRepository(
    SqlAlchemyRepository[RetroTemplate, RetroTemplateORM],
    RetroTemplateRepository,
):
    """SQLAlchemy-реализация RetroTemplateRepository."""

    def __init__(self, session: AsyncSession, mapper: RetroTemplateMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=RetroTemplateORM)

    async def get_system_templates(self) -> list[RetroTemplate]:
        stmt = select(RetroTemplateORM).where(RetroTemplateORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_project(self, project_id: Id) -> list[RetroTemplate]:
        # RetroTemplate не привязан к проекту напрямую — системные шаблоны
        # доступны всем. Кастомные шаблоны привязаны через project_id (если добавится).
        # Пока возвращаем все системные.
        return await self.get_system_templates()

    async def get_by_name(self, name: str) -> RetroTemplate | None:
        stmt = select(RetroTemplateORM).where(RetroTemplateORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None
