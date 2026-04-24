from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


@dataclass
class OAuthLink(BaseEntity):
    """
    Сущность привязки внешнего OAuth/SSO провайдера к аккаунту.

    Принадлежит агрегату UserAuth. Создаётся при привязке
    внешнего провайдера к аккаунту пользователя.

    Атрибуты:
        id: Уникальный идентификатор записи.
        provider: Тип провайдера (Google, Yandex, GitHub, Apple, SAML SSO).
        provider_user_id: ID пользователя у провайдера.
        email: Email пользователя у провайдера (если доступен).
        display_name: Отображаемое имя у провайдера.
        linked_at: Время привязки провайдера.
    """

    provider: AuthProvider = AuthProvider.OAUTH_GOOGLE
    provider_user_id: str = ""
    email: str | None = None
    display_name: str | None = None
    linked_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
