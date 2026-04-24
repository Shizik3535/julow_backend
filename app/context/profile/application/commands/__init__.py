from app.context.profile.application.commands.add_social_link import (
    AddSocialLinkCommand,
    AddSocialLinkHandler,
)
from app.context.profile.application.commands.change_avatar import (
    ChangeAvatarCommand,
    ChangeAvatarHandler,
)
from app.context.profile.application.commands.pin_item import (
    PinItemCommand,
    PinItemHandler,
)
from app.context.profile.application.commands.reorder_pinned_items import (
    ReorderPinnedItemsCommand,
    ReorderPinnedItemsHandler,
)
from app.context.profile.application.commands.remove_social_link import (
    RemoveSocialLinkCommand,
    RemoveSocialLinkHandler,
)
from app.context.profile.application.commands.unpin_item import (
    UnpinItemCommand,
    UnpinItemHandler,
)
from app.context.profile.application.commands.update_appearance import (
    UpdateAppearanceCommand,
    UpdateAppearanceHandler,
)
from app.context.profile.application.commands.update_hotkeys import (
    HotkeyInput,
    UpdateHotkeysCommand,
    UpdateHotkeysHandler,
)
from app.context.profile.application.commands.update_localization import (
    UpdateLocalizationCommand,
    UpdateLocalizationHandler,
)
from app.context.profile.application.commands.update_navigation import (
    UpdateNavigationCommand,
    UpdateNavigationHandler,
)
from app.context.profile.application.commands.update_notifications import (
    TypePreferenceInput,
    UpdateNotificationsCommand,
    UpdateNotificationsHandler,
)
from app.context.profile.application.commands.update_personal_info import (
    UpdatePersonalInfoCommand,
    UpdatePersonalInfoHandler,
)
from app.context.profile.application.commands.update_privacy import (
    UpdatePrivacyCommand,
    UpdatePrivacyHandler,
)
from app.context.profile.application.commands.update_sidebar import (
    SidebarSectionInput,
    UpdateSidebarCommand,
    UpdateSidebarHandler,
)

__all__ = [
    "AddSocialLinkCommand",
    "AddSocialLinkHandler",
    "ChangeAvatarCommand",
    "ChangeAvatarHandler",
    "HotkeyInput",
    "PinItemCommand",
    "PinItemHandler",
    "ReorderPinnedItemsCommand",
    "ReorderPinnedItemsHandler",
    "RemoveSocialLinkCommand",
    "RemoveSocialLinkHandler",
    "SidebarSectionInput",
    "TypePreferenceInput",
    "UnpinItemCommand",
    "UnpinItemHandler",
    "UpdateAppearanceCommand",
    "UpdateAppearanceHandler",
    "UpdateHotkeysCommand",
    "UpdateHotkeysHandler",
    "UpdateLocalizationCommand",
    "UpdateLocalizationHandler",
    "UpdateNavigationCommand",
    "UpdateNavigationHandler",
    "UpdateNotificationsCommand",
    "UpdateNotificationsHandler",
    "UpdatePersonalInfoCommand",
    "UpdatePersonalInfoHandler",
    "UpdatePrivacyCommand",
    "UpdatePrivacyHandler",
    "UpdateSidebarCommand",
    "UpdateSidebarHandler",
]
