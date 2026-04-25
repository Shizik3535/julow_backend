from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.org_branding import OrgBranding
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization


class UpdateOrganizationInfoCommand(BaseCommand):
    """
    Команда обновления информации организации.

    Атрибуты:
        org_id: ID организации.
        name: Новое название (None — без изменений).
        personalization_color: Акцентный цвет (#RRGGBB).
        personalization_icon_url: URL иконки.
        personalization_display_name: Отображаемое имя.
        personalization_custom_domain: Кастомный домен.
        branding_logo_url: URL логотипа.
        branding_favicon_url: URL фавикона.
        branding_custom_css: Пользовательский CSS.
        branding_login_message: Сообщение на странице входа.
    """

    caller_id: str
    org_id: str
    name: str | None = None
    personalization_color: str | None = None
    personalization_icon_url: str | None = None
    personalization_display_name: str | None = None
    personalization_custom_domain: str | None = None
    branding_logo_url: str | None = None
    branding_favicon_url: str | None = None
    branding_custom_css: str | None = None
    branding_login_message: str | None = None


class UpdateOrganizationInfoHandler(BaseCommandHandler[UpdateOrganizationInfoCommand, None]):
    """
    Обработчик обновления информации организации.

    Конвертирует примитивы в VO OrgPersonalization, вызывает
    доменный метод update_info.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateOrganizationInfoCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        personalization: OrgPersonalization | None = None
        has_pers = any([
            command.personalization_color is not None,
            command.personalization_icon_url is not None,
            command.personalization_display_name is not None,
            command.personalization_custom_domain is not None,
            command.branding_logo_url is not None,
            command.branding_favicon_url is not None,
            command.branding_custom_css is not None,
            command.branding_login_message is not None,
        ])
        if has_pers:
            branding: OrgBranding | None = None
            has_branding = any([
                command.branding_logo_url is not None,
                command.branding_favicon_url is not None,
                command.branding_custom_css is not None,
                command.branding_login_message is not None,
            ])
            if has_branding:
                old_branding = org.personalization.branding
                branding = OrgBranding(
                    logo_url=Url(command.branding_logo_url) if command.branding_logo_url is not None else (old_branding.logo_url if old_branding else None),
                    favicon_url=Url(command.branding_favicon_url) if command.branding_favicon_url is not None else (old_branding.favicon_url if old_branding else None),
                    custom_css=command.branding_custom_css if command.branding_custom_css is not None else (old_branding.custom_css if old_branding else None),
                    login_message=command.branding_login_message if command.branding_login_message is not None else (old_branding.login_message if old_branding else None),
                )

            personalization = OrgPersonalization(
                color=AccentColor(hex=command.personalization_color) if command.personalization_color is not None else org.personalization.color,
                icon_url=Url(command.personalization_icon_url) if command.personalization_icon_url is not None else org.personalization.icon_url,
                display_name=command.personalization_display_name if command.personalization_display_name is not None else org.personalization.display_name,
                custom_domain=command.personalization_custom_domain if command.personalization_custom_domain is not None else org.personalization.custom_domain,
                branding=branding if branding is not None else org.personalization.branding,
            )

        org.update_info(name=command.name, personalization=personalization)
        await self._org_repo.update(org)
        await self._event_bus.publish_all(org.clear_domain_events())
