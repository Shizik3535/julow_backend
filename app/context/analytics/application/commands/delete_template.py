from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardTemplateNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)


class DeleteTemplateCommand(BaseCommand):
    """Удалить пользовательский шаблон. Системные удалять нельзя
    (``CannotDeleteSystemTemplateException``).
    """

    caller_id: str
    workspace_id: str
    template_id: str


class DeleteTemplateHandler(BaseCommandHandler[DeleteTemplateCommand, None]):
    REQUIRED_PERMISSION = "analytics.admin"

    def __init__(
        self,
        template_repo: DashboardTemplateRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = template_repo
        self._permission_checker = permission_checker

    async def handle(self, command: DeleteTemplateCommand) -> None:
        template = await self._repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise DashboardTemplateNotFoundException(id=command.template_id)
        # Кастомные шаблоны видны/удаляемы только в своём workspace; чтобы не
        # подсказывать существование чужого шаблона — отвечаем «не найдено».
        # Системные шаблоны (workspace_id is None) глобальны и блокируются
        # ниже через assert_deletable().
        if not template.is_system and (
            template.workspace_id is None
            or str(template.workspace_id) != command.workspace_id
        ):
            raise DashboardTemplateNotFoundException(id=command.template_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        template.assert_deletable()  # бросит CannotDeleteSystemTemplateException для системных
        await self._repo.delete(template.id)
