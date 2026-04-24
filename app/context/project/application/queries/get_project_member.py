from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_member_dto import ProjectMemberDTO
from app.context.project.application.exceptions.membership_app_exceptions import MemberNotInProjectException
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository


class GetProjectMemberQuery(BaseQuery):
    """Запрос получения конкретного участника проекта."""

    project_id: str
    user_id: str


class GetProjectMemberHandler(BaseQueryHandler[GetProjectMemberQuery, ProjectMemberDTO]):
    """Обработчик получения конкретного участника проекта."""

    def __init__(self, membership_repo: ProjectMembershipRepository) -> None:
        super().__init__()
        self._membership_repo = membership_repo

    async def handle(self, query: GetProjectMemberQuery) -> ProjectMemberDTO:
        member = await self._membership_repo.get_member_by_project_and_user(
            project_id=Id.from_string(query.project_id),
            user_id=Id.from_string(query.user_id),
        )
        if member is None:
            raise MemberNotInProjectException(query.user_id, query.project_id)

        return ProjectMemberDTO(
            id=str(member.id),
            user_id=str(member.user_id),
            role_id=str(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
        )
