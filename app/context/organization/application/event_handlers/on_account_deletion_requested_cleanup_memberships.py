from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class OnAccountDeletionRequestedCleanupMemberships(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события AccountDeletionRequested из Identity BC.

    Подписывается на топик «identity.events» и реагирует
    на событие «AccountDeletionRequested»: удаляет пользователя
    из всех организаций, где он является участником.

    Идемпотентность: повторный вызов безопасен — если участник
    уже удалён, операция пропускается.
    """

    def __init__(self, membership_repo: OrgMembershipRepository) -> None:
        super().__init__()
        self._membership_repo = membership_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "AccountDeletionRequested":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning(
                "AccountDeletionRequested event missing user_id",
                event_data=event,
            )
            return

        user_id = Id.from_string(user_id_str)
        members = await self._membership_repo.get_members_by_org(user_id)

        if not members:
            self._logger.info(
                "User has no memberships to cleanup",
                user_id=user_id_str,
            )
            return

        for member in members:
            membership = await self._membership_repo.get_by_org_id(member.user_id)
            if membership is None:
                continue

            try:
                membership.remove_member(user_id=user_id, is_owner=False)
                await self._membership_repo.update(membership)
            except Exception:
                self._logger.warning(
                    "Failed to remove member from org during account deletion cleanup",
                    user_id=user_id_str,
                    org_member_id=str(member.id),
                    exc_info=True,
                )

        self._logger.info(
            "Cleaned up memberships for deleted user",
            user_id=user_id_str,
        )
