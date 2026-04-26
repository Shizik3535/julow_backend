from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationDTO, InvitationListDTO
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository


class SearchMyInvitationsQuery(BaseQuery):
    """
    Запрос «моих приглашений» в организации.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        offset: Смещение.
        limit: Лимит.
        filters: Фильтры (status, org_id, search_text).
    """

    caller_id: str
    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchMyInvitationsHandler(BaseQueryHandler[SearchMyInvitationsQuery, InvitationListDTO]):
    """
    Обработчик поиска «моих приглашений».

    Ищет PENDING приглашения по email пользователя
    и ACCEPTED/DECLINED по user_id.
    Не требует прав на конкретную организацию.
    """

    def __init__(
        self,
        invitation_repo: InvitationRepository,
        identity_port: IdentityUserPort,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._identity_port = identity_port

    async def handle(self, query: SearchMyInvitationsQuery) -> InvitationListDTO:
        caller_id = Id.from_string(query.caller_id)

        user_data = await self._identity_port.get_user(query.caller_id)
        if user_data is None:
            return InvitationListDTO(items=[], total=0)

        email = user_data.get("email", "")
        if not email:
            return InvitationListDTO(items=[], total=0)

        invitations, total = await self._invitation_repo.search_by_user(
            email=email,
            user_id=caller_id,
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )

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
                user_id=str(inv.user_id) if inv.user_id else None,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
            for inv in invitations
        ]
        return InvitationListDTO(items=items, total=total)
