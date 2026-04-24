from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)


class UpdateRetroTemplateCommand(BaseCommand):
    """
    Команда обновления шаблона ретроспективы.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        template_id: ID шаблона.
        sections: Секции [{"title": str, "prompt": str | None, "item_type": str}].
    """

    caller_id: str
    workspace_id: str
    template_id: str
    sections: list[dict] | None = None


class UpdateRetroTemplateHandler(BaseCommandHandler[UpdateRetroTemplateCommand, None]):
    """Обработчик обновления шаблона ретроспективы."""

    REQUIRED_PERMISSION = "projects.retro_templates.write"

    def __init__(self, retro_template_repo: RetroTemplateRepository, workspace_permission_checker: WorkspacePermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._retro_template_repo = retro_template_repo
        self._workspace_permission_checker = workspace_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateRetroTemplateCommand) -> None:
        await self._workspace_permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        template = await self._retro_template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise ValueError(f"Шаблон ретроспективы не найден: {command.template_id}")

        sections: list[RetroSection] | None = None
        if command.sections is not None:
            sections = [
                RetroSection(
                    title=s["title"],
                    prompt=s.get("prompt"),
                    item_type=RetroItemType(s["item_type"]),
                )
                for s in command.sections
            ]

        template.update(sections=sections)
        await self._retro_template_repo.update(template)
        await self._event_bus.publish_all(template.clear_domain_events())
