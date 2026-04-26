from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationDTO, InvitationListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GetInvitationsByOrgQuery(BaseQuery):
    """
    Запрос приглашений организации.

    Атрибуты:
        org_id: ID организации.
    """

    caller_id: str
    org_id: str


class GetInvitationsByOrgHandler(BaseQueryHandler[GetInvitationsByOrgQuery, InvitationListDTO]):
    """Обработчик запроса приглашений организации."""

    REQUIRED_PERMISSION = "invitations.read"

    def __init__(self, invitation_repo: InvitationRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetInvitationsByOrgQuery) -> InvitationListDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)
        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        invitations = await self._invitation_repo.get_by_org_id(org_id)

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
        return InvitationListDTO(items=items, total=len(items))
