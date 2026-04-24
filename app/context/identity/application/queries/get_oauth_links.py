from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.oauth_link_dto import OAuthLinkDTO
from app.context.identity.application.dto.oauth_link_list_dto import OAuthLinkListDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class GetOAuthLinksQuery(BaseQuery):
    """
    Запрос списка привязанных OAuth-провайдеров.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class GetOAuthLinksHandler(BaseQueryHandler[GetOAuthLinksQuery, OAuthLinkListDTO]):
    """
    Обработчик запроса привязанных OAuth-провайдеров.
    """

    def __init__(self, user_auth_repo: UserAuthRepository) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo

    async def handle(self, query: GetOAuthLinksQuery) -> OAuthLinkListDTO:
        user_id = Id.from_string(query.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(query.user_id)

        items = [
            OAuthLinkDTO(
                provider=link.provider.value,
                provider_user_id=link.provider_user_id,
                email=link.email,
                display_name=link.display_name,
                linked_at=link.linked_at,
            )
            for link in user_auth.oauth_links
        ]

        return OAuthLinkListDTO(items=items, total=len(items))
