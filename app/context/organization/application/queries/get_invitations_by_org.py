from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationDTO, InvitationListDTO
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository


class GetInvitationsByOrgQuery(BaseQuery):
    """
    Запрос приглашений организации.

    Атрибуты:
        org_id: ID организации.
    """

    org_id: str


class GetInvitationsByOrgHandler(BaseQueryHandler[GetInvitationsByOrgQuery, InvitationListDTO]):
    """Обработчик запроса приглашений организации."""

    def __init__(self, invitation_repo: InvitationRepository) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo

    async def handle(self, query: GetInvitationsByOrgQuery) -> InvitationListDTO:
        invitations = await self._invitation_repo.get_by_org_id(Id.from_string(query.org_id))

        items = [
            InvitationDTO(
                id=str(inv.id),
                org_id=str(inv.org_id),
                email=str(inv.email) if inv.email else None,
                link=(
                    {
                        "value": inv.link.value,
                        "expires_at": inv.link.expires_at.isoformat() if inv.link.expires_at else None,
                        "max_uses": inv.link.max_uses,
                        "used_count": inv.link.used_count,
                    }
                    if inv.link
                    else None
                ),
                role_id=str(inv.role_id),
                invited_by=str(inv.invited_by),
                invited_at=inv.invited_at,
                status=inv.status.value,
                approved_by=str(inv.approved_by) if inv.approved_by else None,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
            for inv in invitations
        ]
        return InvitationListDTO(items=items, total=len(items))
