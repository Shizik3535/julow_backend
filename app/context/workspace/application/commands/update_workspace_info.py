from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding
from app.context.workspace.domain.value_objects.workspace_personalization import WorkspacePersonalization


class UpdateWorkspaceInfoCommand(BaseCommand):
    """
    Команда обновления информации workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        name: Новое название.
        color: Акцентный цвет (hex).
        icon_url: URL иконки.
        display_name: Отображаемое имя.
        description: Описание.
        logo_url: URL логотипа (branding).
        cover_image_url: URL обложки (branding).
        custom_css: Кастомный CSS (branding).
    """

    caller_id: str
    workspace_id: str
    name: str | None = None
    color: str | None = None
    icon_url: str | None = None
    display_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    cover_image_url: str | None = None
    custom_css: str | None = None


class UpdateWorkspaceInfoHandler(BaseCommandHandler[UpdateWorkspaceInfoCommand, None]):
    """
    Обработчик обновления информации workspace.

    Собирает WorkspacePersonalization из примитивов, вызывает update_info.
    """

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateWorkspaceInfoCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        personalization: WorkspacePersonalization | None = None
        has_pers = any([
            command.color is not None,
            command.icon_url is not None,
            command.display_name is not None,
            command.description is not None,
            command.logo_url is not None,
            command.cover_image_url is not None,
            command.custom_css is not None,
        ])
        if has_pers:
            branding: WorkspaceBranding | None = None
            has_branding = any([command.logo_url, command.cover_image_url, command.custom_css])
            if has_branding:
                branding = WorkspaceBranding(
                    logo_url=Url(command.logo_url) if command.logo_url else (ws.personalization.branding.logo_url if ws.personalization.branding else None),
                    cover_image_url=Url(command.cover_image_url) if command.cover_image_url else (ws.personalization.branding.cover_image_url if ws.personalization.branding else None),
                    custom_css=command.custom_css if command.custom_css is not None else (ws.personalization.branding.custom_css if ws.personalization.branding else None),
                )
            else:
                branding = ws.personalization.branding

            personalization = WorkspacePersonalization(
                color=Color(command.color) if command.color else ws.personalization.color,
                icon_url=Url(command.icon_url) if command.icon_url else ws.personalization.icon_url,
                display_name=command.display_name if command.display_name is not None else ws.personalization.display_name,
                description=command.description if command.description is not None else ws.personalization.description,
                branding=branding,
            )

        ws.update_info(name=command.name, personalization=personalization)
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
