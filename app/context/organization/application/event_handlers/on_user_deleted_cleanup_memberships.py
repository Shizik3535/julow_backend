from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class OnUserDeletedCleanupMemberships(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserDeleted из Identity BC.

    Окончательно удаляет пользователя из всех организаций.
    Подписывается на топик «identity.events».
    """

    def __init__(self, membership_repo: OrgMembershipRepository) -> None:
        super().__init__()
        self._membership_repo = membership_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserDeleted":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning("UserDeleted missing user_id", raw_event=event)
            return

        user_id = Id.from_string(user_id_str)
        memberships = await self._membership_repo.get_by_user_id(user_id)
        for membership in memberships:
            membership.remove_member(user_id=user_id, is_owner=False)
            await self._membership_repo.update(membership)

        self._logger.info(
            "Cleaned up org memberships for deleted user",
            user_id=str(user_id),
            count=len(memberships),
        )
