from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.sidebar_section import SidebarSection


class SidebarSectionInput(BaseCommand):
    """
    Входные данные для одной секции sidebar.

    Атрибуты:
        section_id: Идентификатор секции.
        is_collapsed: Свернута ли секция.
        item_ids: Список ID элементов внутри секции.
        order: Порядок секции в sidebar.
    """

    section_id: str
    is_collapsed: bool = False
    item_ids: list[str] = []
    order: int = 0


class UpdateSidebarCommand(BaseCommand):
    """
    Команда обновления конфигурации sidebar.

    Атрибуты:
        user_id: ID пользователя.
        sections: Список секций sidebar.
    """

    user_id: str
    sections: list[SidebarSectionInput]


class UpdateSidebarHandler(BaseCommandHandler[UpdateSidebarCommand, None]):
    """
    Обработчик обновления sidebar.

    Преобразует входные данные в доменные VO и вызывает
    update_sidebar на агрегате.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateSidebarCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        sections = [
            SidebarSection(
                section_id=s.section_id,
                is_collapsed=s.is_collapsed,
                item_ids=[Id.from_string(iid) for iid in s.item_ids],
                order=s.order,
            )
            for s in command.sections
        ]

        profile.update_sidebar(sections)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
