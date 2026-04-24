from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction
from app.context.profile.domain.value_objects.hotkey_config import HotkeyConfig


class HotkeyInput(BaseCommand):
    """
    Входные данные для одной горячей клавиши.

    Атрибуты:
        action: Действие (например CREATE_TASK, SEARCH).
        key_combination: Комбинация клавиш (например Ctrl+K).
        is_enabled: Включена ли горячая клавиша.
    """

    action: str
    key_combination: str
    is_enabled: bool = True


class UpdateHotkeysCommand(BaseCommand):
    """
    Команда обновления конфигурации горячих клавиш.

    Атрибуты:
        user_id: ID пользователя.
        hotkeys: Список конфигураций горячих клавиш.
    """

    user_id: str
    hotkeys: list[HotkeyInput]


class UpdateHotkeysHandler(BaseCommandHandler[UpdateHotkeysCommand, None]):
    """
    Обработчик обновления горячих клавиш.

    Преобразует входные данные в доменные VO и вызывает
    update_hotkeys на агрегате.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateHotkeysCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        configs = [
            HotkeyConfig(
                action=HotkeyAction(h.action),
                key_combination=h.key_combination,
                is_enabled=h.is_enabled,
            )
            for h in command.hotkeys
        ]

        profile.update_hotkeys(configs)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
