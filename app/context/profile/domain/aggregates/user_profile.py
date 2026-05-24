from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.hotkey_config import HotkeyConfig
from app.context.profile.domain.value_objects.sidebar_section import SidebarSection
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType
from app.context.profile.domain.entities.pinned_item import PinnedItem
from app.context.profile.domain.entities.social_link import SocialLink
from app.context.profile.domain.events.profile_events import (
    AppearanceSettingsChanged,
    AvatarChanged,
    HotkeysChanged,
    LocalizationSettingsChanged,
    NavigationSettingsChanged,
    PersonalInfoChanged,
    PinnedItemAdded,
    PinnedItemRemoved,
    PrivacySettingsChanged,
    ProfileCreated,
    ProfileDeleted,
    SidebarConfigUpdated,
)
from app.shared.domain.changed_fields import changed_fields
from app.context.profile.domain.exceptions.profile_exceptions import (
    DuplicatePinnedItemException,
    DuplicateSocialLinkException,
)


@dataclass
class UserProfile(AggregateRoot):
    """
    Корень агрегата профиля пользователя (Profile BC).

    Один AR на пользователя. Настройки организованы в VO-группы —
    добавление новой настройки = поле в VO, а не новый метод на AR.

    Атрибуты:
        user_id: Opaque ID из Identity BC.
        avatar_url: URL аватара.
        bio: О себе.
        job_title: Должность.
        social_links: Социальные ссылки.
        appearance: Настройки внешнего вида.
        localization: Настройки локализации.
        navigation: Настройки навигации.
        privacy: Настройки приватности.
        hotkeys: Конфигурация горячих клавиш.
        sidebar_sections: Секции sidebar.
        pinned_items: Закреплённые элементы.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    display_name: str | None = None
    avatar_url: Url | None = None
    bio: str | None = None
    job_title: str | None = None
    social_links: list[SocialLink] = field(default_factory=list)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    localization: LocalizationSettings = field(default_factory=LocalizationSettings)
    navigation: NavigationSettings = field(default_factory=NavigationSettings)
    privacy: PrivacySettings = field(default_factory=PrivacySettings)
    hotkeys: list[HotkeyConfig] = field(default_factory=list)
    sidebar_sections: list[SidebarSection] = field(default_factory=list)
    pinned_items: list[PinnedItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, user_id: Id) -> UserProfile:
        """Создаёт профиль со всеми настройками по умолчанию."""
        profile = cls(user_id=user_id)
        profile._register_event(
            ProfileCreated(user_id=str(user_id))
        )
        return profile

    # --- Аватар ---

    def change_avatar(self, url: Url) -> None:
        """Изменяет аватар."""
        self.avatar_url = url
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AvatarChanged(user_id=str(self.user_id))
        )

    # --- Персональные данные ---

    def update_personal_info(
        self,
        display_name: str | None = None,
        bio: str | None = None,
        job_title: str | None = None,
    ) -> None:
        """Изменяет только переданные персональные поля."""
        changed: list[str] = []
        if display_name is not None and self.display_name != display_name:
            self.display_name = display_name
            changed.append("display_name")
        if bio is not None and self.bio != bio:
            self.bio = bio
            changed.append("bio")
        if job_title is not None and self.job_title != job_title:
            self.job_title = job_title
            changed.append("job_title")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                PersonalInfoChanged(user_id=str(self.user_id), changed_fields=changed)
            )

    # --- Социальные ссылки ---

    def add_social_link(self, platform: str, url: Url, display_name: str | None = None) -> None:
        """Добавляет социальную ссылку. Инвариант: уникальность по platform."""
        if any(sl.platform == platform for sl in self.social_links):
            raise DuplicateSocialLinkException(platform)
        link = SocialLink(platform=platform, url=url, display_name=display_name)
        self.social_links.append(link)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PersonalInfoChanged(
                user_id=str(self.user_id),
                changed_fields=["social_links"],
            )
        )

    def remove_social_link(self, platform: str) -> None:
        """Удаляет социальную ссылку по платформе."""
        self.social_links = [sl for sl in self.social_links if sl.platform != platform]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PersonalInfoChanged(
                user_id=str(self.user_id),
                changed_fields=["social_links"],
            )
        )

    # --- Настройки внешнего вида ---

    def update_appearance(self, settings: AppearanceSettings) -> None:
        """Заменяет группу настроек внешнего вида."""
        changed = changed_fields(self.appearance, settings)
        self.appearance = settings
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                AppearanceSettingsChanged(
                    user_id=str(self.user_id),
                    changed_fields=changed,
                )
            )

    # --- Настройки локализации ---

    def update_localization(self, settings: LocalizationSettings) -> None:
        """Заменяет группу настроек локализации."""
        changed = changed_fields(self.localization, settings)
        self.localization = settings
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                LocalizationSettingsChanged(
                    user_id=str(self.user_id),
                    changed_fields=changed,
                )
            )

    # --- Настройки навигации ---

    def update_navigation(self, settings: NavigationSettings) -> None:
        """Заменяет группу настроек навигации."""
        changed = changed_fields(self.navigation, settings)
        self.navigation = settings
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                NavigationSettingsChanged(
                    user_id=str(self.user_id),
                    changed_fields=changed,
                )
            )

    # --- Настройки приватности ---

    def update_privacy(self, settings: PrivacySettings) -> None:
        """Заменяет группу настроек приватности."""
        changed = changed_fields(self.privacy, settings)
        self.privacy = settings
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                PrivacySettingsChanged(
                    user_id=str(self.user_id),
                    changed_fields=changed,
                )
            )

    # --- Горячие клавиши ---

    def update_hotkeys(self, configs: list[HotkeyConfig]) -> None:
        """Заменяет конфигурацию горячих клавиш."""
        self.hotkeys = configs
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            HotkeysChanged(user_id=str(self.user_id))
        )

    # --- Sidebar ---

    def update_sidebar(self, sections: list[SidebarSection]) -> None:
        """Заменяет конфигурацию sidebar."""
        self.sidebar_sections = sections
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SidebarConfigUpdated(user_id=str(self.user_id))
        )

    # --- Закреплённые элементы ---

    def pin_item(self, target_type: PinnedTargetType, target_id: Id) -> None:
        """Закрепляет элемент. Инвариант: уникальность по (target_type, target_id)."""
        if any(
            pi.target_type == target_type and pi.target_id == target_id
            for pi in self.pinned_items
        ):
            raise DuplicatePinnedItemException(
                target_type=target_type.value,
                target_id=str(target_id),
            )
        order = len(self.pinned_items)
        item = PinnedItem(target_type=target_type, target_id=target_id, order=order)
        self.pinned_items.append(item)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PinnedItemAdded(
                user_id=str(self.user_id),
                target_type=target_type,
                target_id=str(target_id),
            )
        )

    def unpin_item(self, target_type: PinnedTargetType, target_id: Id) -> None:
        """Открепляет элемент."""
        self.pinned_items = [
            pi for pi in self.pinned_items
            if not (pi.target_type == target_type and pi.target_id == target_id)
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PinnedItemRemoved(
                user_id=str(self.user_id),
                target_type=target_type,
                target_id=str(target_id),
            )
        )

    def reorder_pinned_items(self, ordered_ids: list[Id]) -> None:
        """Переупорядочивает закреплённые элементы по списку target_id."""
        id_to_order = {item_id: i for i, item_id in enumerate(ordered_ids)}
        for pi in self.pinned_items:
            if pi.target_id in id_to_order:
                pi.order = id_to_order[pi.target_id]
        self.pinned_items.sort(key=lambda pi: pi.order)
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Удаление ---

    def delete(self) -> None:
        """Помечает профиль как удалённый."""
        self._register_event(
            ProfileDeleted(user_id=str(self.user_id))
        )
