from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.organization.application.dto.invitation_dto import InvitationDTO
from app.context.organization.domain.exceptions.invitation_exceptions import InvitationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository


class GetInvitationByTokenQuery(BaseQuery):
    """
    Запрос приглашения по токену ссылки.

    Атрибуты:
        token: Значение токена.
    """

    token: str


class GetInvitationByTokenHandler(BaseQueryHandler[GetInvitationByTokenQuery, InvitationDTO]):
    """Обработчик запроса приглашения по токену."""

    def __init__(self, invitation_repo: InvitationRepository) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo

    async def handle(self, query: GetInvitationByTokenQuery) -> InvitationDTO:
        invitation = await self._invitation_repo.get_by_token(query.token)
        if invitation is None:
            raise InvitationNotFoundException(query.token)

        return InvitationDTO(
            id=str(invitation.id),
            org_id=str(invitation.org_id),
            email=str(invitation.email) if invitation.email else None,
            link=(
                {
                    "value": invitation.link.value,
                    "expires_at": invitation.link.expires_at.isoformat() if invitation.link.expires_at else None,
                    "max_uses": invitation.link.max_uses,
                    "used_count": invitation.link.used_count,
                }
                if invitation.link
                else None
            ),
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            approved_by=str(invitation.approved_by) if invitation.approved_by else None,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
