from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.project.application.dto.retro_template_dto import RetroTemplateDTO
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)


class CreateRetroTemplateCommand(BaseCommand):
    """
    Команда создания шаблона ретроспективы.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        name: Название шаблона.
        sections: Секции [{"title": str, "prompt": str | None, "item_type": str}].
    """

    caller_id: str
    workspace_id: str
    name: str
    sections: list[dict]


class CreateRetroTemplateHandler(BaseCommandHandler[CreateRetroTemplateCommand, RetroTemplateDTO]):
    """Обработчик создания шаблона ретроспективы."""
    REQUIRED_PERMISSION = "projects.retro_templates.write"

    def __init__(self, retro_template_repo: RetroTemplateRepository, workspace_permission_checker: WorkspacePermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._retro_template_repo = retro_template_repo
        self._workspace_permission_checker = workspace_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateRetroTemplateCommand) -> RetroTemplateDTO:
        await self._workspace_permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        sections = [
            RetroSection(
                title=s["title"],
                prompt=s.get("prompt"),
                item_type=RetroItemType(s["item_type"]),
            )
            for s in command.sections
        ]
        template = RetroTemplate.create_custom(name=command.name, sections=sections)
        await self._retro_template_repo.add(template)
        await self._event_bus.publish_all(template.clear_domain_events())

        return RetroTemplateDTO(
            id=str(template.id),
            name=template.name,
            sections=[
                {"title": s.title, "prompt": s.prompt, "item_type": s.item_type.value}
                for s in template.sections
            ],
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
