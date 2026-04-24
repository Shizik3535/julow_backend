from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.changelog_entry_dto import ChangelogEntryDTO, ChangelogListDTO
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository


class GetTaskChangelogByFieldQuery(BaseQuery):
    """
    Запрос истории изменений конкретного поля задачи.

    Атрибуты:
        task_id: ID задачи.
        field_name: Имя поля.
    """

    task_id: str
    field_name: str


class GetTaskChangelogByFieldHandler(BaseQueryHandler[GetTaskChangelogByFieldQuery, ChangelogListDTO]):
    """Обработчик получения истории изменений конкретного поля."""

    def __init__(self, changelog_repo: ChangelogRepository) -> None:
        super().__init__()
        self._changelog_repo = changelog_repo

    async def handle(self, query: GetTaskChangelogByFieldQuery) -> ChangelogListDTO:
        entries = await self._changelog_repo.get_by_task_and_field(
            task_id=Id.from_string(query.task_id),
            field_name=query.field_name,
        )
        items = [
            ChangelogEntryDTO(
                id=str(e.id),
                task_id=str(e.task_id),
                field_name=e.field_name,
                old_value=e.old_value,
                new_value=e.new_value,
                changed_by=str(e.changed_by),
                changed_at=e.changed_at,
            )
            for e in entries
        ]
        return ChangelogListDTO(items=items, total=len(items))
