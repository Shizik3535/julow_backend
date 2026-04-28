from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.profile.application.dto.profile_dto import ProfileDTO
from app.context.profile.application.dto.profile_list_dto import ProfileListDTO
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class SearchProfilesQuery(BaseQuery):
    """
    Запрос поиска профилей с пагинацией и фильтрацией.

    Атрибуты:
        offset: Смещение для пагинации.
        limit: Максимальное количество записей.
        filters: Словарь фильтров {поле: значение}.
    """

    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchProfilesHandler(BaseQueryHandler[SearchProfilesQuery, ProfileListDTO]):
    """
    Обработчик поиска профилей.

    Загружает список профилей через репозиторий и маппит в ProfileListDTO.
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        super().__init__()
        self._profile_repo = profile_repo

    async def handle(self, query: SearchProfilesQuery) -> ProfileListDTO:
        profiles = await self._profile_repo.search(
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )

        items = [_map_profile(p) for p in profiles]
        return ProfileListDTO(items=items, total=len(items))


def _map_profile(profile: Any) -> ProfileDTO:
    """Маппинг агрегата UserProfile в ProfileDTO."""
    return ProfileDTO(
        id=str(profile.id),
        user_id=str(profile.user_id),
        avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
        bio=profile.bio,
        job_title=profile.job_title,
        social_links=[
            {"platform": sl.platform, "url": str(sl.url), "display_name": sl.display_name}
            for sl in profile.social_links
        ],
        appearance={
            "theme": profile.appearance.theme.value,
            "accent_color": str(profile.appearance.accent_color),
            "interface_density": profile.appearance.interface_density.value,
            "custom_theme": (
                {
                    "name": profile.appearance.custom_theme.name,
                    "colors": {k: str(v) for k, v in profile.appearance.custom_theme.colors.items()},
                }
                if profile.appearance.custom_theme
                else None
            ),
        },
        localization={
            "language": str(profile.localization.language),
            "timezone": str(profile.localization.timezone),
            "date_format": str(profile.localization.date_format),
            "time_format": profile.localization.time_format.value,
            "week_start_day": profile.localization.week_start_day.value,
        },
        navigation={
            "start_page": str(profile.navigation.start_page),
        },
        privacy={
            "profile_visibility": profile.privacy.profile_visibility.value,
            "online_status_visibility": profile.privacy.online_status_visibility.value,
            "activity_tracking_consent": profile.privacy.activity_tracking_consent.value,
        },
        hotkeys=[
            {"action": hk.action.value, "key_combination": hk.key_combination, "is_enabled": hk.is_enabled}
            for hk in profile.hotkeys
        ],
        sidebar_sections=[
            {
                "section_id": ss.section_id,
                "is_collapsed": ss.is_collapsed,
                "item_ids": [str(iid) for iid in ss.item_ids],
                "order": ss.order,
            }
            for ss in profile.sidebar_sections
        ],
        pinned_items=[
            {
                "target_type": pi.target_type.value,
                "target_id": str(pi.target_id),
                "order": pi.order,
                "pinned_at": pi.pinned_at.isoformat(),
            }
            for pi in profile.pinned_items
        ],
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
