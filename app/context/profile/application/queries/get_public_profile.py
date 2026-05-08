from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.dto.public_profile_dto import PublicProfileDTO
from app.context.profile.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility


class GetPublicProfileQuery(BaseQuery):
    """
    Запрос публичного профиля другого пользователя по user_id.

    Видимость определяется настройкой privacy.profile_visibility владельца профиля:
        - PUBLIC: доступен всем аутентифицированным пользователям.
        - ORGANIZATION_ONLY: доступен, если запрашивающий состоит в общей организации.
        - PRIVATE: доступен только владельцу.

    При отсутствии прав на просмотр возвращается ProfileNotFoundException
    (404), чтобы не раскрывать сам факт существования профиля (anti-enumeration).

    Атрибуты:
        user_id: Идентификатор владельца запрашиваемого профиля.
        requester_id: Идентификатор пользователя, выполняющего запрос.
    """

    user_id: str
    requester_id: str


class GetPublicProfileHandler(BaseQueryHandler[GetPublicProfileQuery, PublicProfileDTO]):
    """
    Обработчик запроса публичного профиля.

    Загружает профиль по user_id, проверяет что профиль открыт,
    и преобразует в PublicProfileDTO (только публичные данные).
    """

    def __init__(
        self,
        profile_repo: UserProfileRepository,
        org_membership_port: OrganizationMembershipPort,
    ) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._org_membership_port = org_membership_port

    async def handle(self, query: GetPublicProfileQuery) -> PublicProfileDTO:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(query.user_id))
        if profile is None:
            raise ProfileNotFoundException(query.user_id)

        if not await self._is_visible(profile, query.requester_id):
            # Не раскрываем существование скрытого профиля.
            raise ProfileNotFoundException(query.user_id)

        return PublicProfileDTO(
            id=str(profile.id),
            user_id=str(profile.user_id),
            avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
            bio=profile.bio,
            job_title=profile.job_title,
            social_links=[
                {"platform": sl.platform, "url": str(sl.url), "display_name": sl.display_name}
                for sl in profile.social_links
            ],
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def _is_visible(self, profile, requester_id: str) -> bool:
        """Определяет, имеет ли запрашивающий право видеть профиль."""
        # Владелец всегда видит свой профиль.
        if str(profile.user_id) == requester_id:
            return True

        visibility = profile.privacy.profile_visibility
        if visibility == ProfileVisibility.PUBLIC:
            return True
        if visibility == ProfileVisibility.ORGANIZATION_ONLY:
            return await self._org_membership_port.share_organization(
                user_id_a=requester_id,
                user_id_b=str(profile.user_id),
            )
        # PRIVATE и любые будущие значения — недоступно.
        return False
