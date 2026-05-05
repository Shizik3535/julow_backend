from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository


class OnSSOUserProvisionedAddMember(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события SSOUserProvisioned из Identity BC.

    Автоматически добавляет пользователя в организацию с ролью по умолчанию
    при auto-provisioning через SSO.

    Подписывается на топик «identity.events».
    """

    def __init__(
        self,
        membership_repo: OrgMembershipRepository,
        org_role_repo: OrgRoleRepository,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._org_role_repo = org_role_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "SSOUserProvisioned":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        org_id_str = payload.get("org_id")
        default_role_id_str = payload.get("default_role_id")

        if not user_id_str or not org_id_str:
            self._logger.warning(
                "SSOUserProvisioned missing user_id or org_id",
                raw_event=event,
            )
            return

        user_id = Id.from_string(user_id_str)
        org_id = Id.from_string(org_id_str)

        # Проверяем, не состоит ли уже пользователь в организации
        existing_member = await self._membership_repo.get_member_by_org_and_user(org_id, user_id)
        if existing_member is not None:
            self._logger.info(
                "User already member of organization, skipping auto-provision",
                user_id=str(user_id),
                org_id=str(org_id),
            )
            return

        # Получаем агрегат членства организации
        membership = await self._membership_repo.get_by_org_id(org_id)
        if membership is None:
            self._logger.warning(
                "OrgMembership aggregate not found for org",
                org_id=str(org_id),
            )
            return

        # Определяем роль по умолчанию
        role_id: Id | None = None
        if default_role_id_str:
            role_id = Id.from_string(default_role_id_str)
        else:
            default_role = await self._org_role_repo.get_by_name(org_id, "member")
            if default_role is not None:
                role_id = default_role.id

        if role_id is None:
            self._logger.warning(
                "No default role found for SSO auto-provision",
                org_id=str(org_id),
            )
            return

        # Добавляем участника
        membership.add_member(user_id=user_id, role_id=role_id)
        await self._membership_repo.update(membership)

        self._logger.info(
            "Auto-provisioned SSO user into organization",
            user_id=str(user_id),
            org_id=str(org_id),
            role_id=str(role_id),
        )
