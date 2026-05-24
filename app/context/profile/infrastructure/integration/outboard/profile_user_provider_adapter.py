from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.dto.profile_dto import ProfileDTO
from app.context.profile.application.ports.integration.outboard.profile_user_provider import (
    ProfileUserProvider,
)
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class ProfileUserProviderAdapter(ProfileUserProvider):
    """
    Реализация ProfileUserProvider.

    Предоставляет публичный профиль пользователя другим BC
    через синхронный DI-порт.
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def get_profile(self, user_id: str) -> ProfileDTO | None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(user_id))
        if profile is None:
            return None
        return ProfileDTO(
            id=str(profile.id),
            user_id=str(profile.user_id),
            display_name=profile.display_name,
            avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
            bio=profile.bio,
            job_title=profile.job_title,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def get_profiles(self, user_ids: list[str]) -> list[ProfileDTO]:
        result: list[ProfileDTO] = []
        for uid in user_ids:
            dto = await self.get_profile(uid)
            if dto is not None:
                result.append(dto)
        return result
