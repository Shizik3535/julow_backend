from __future__ import annotations

from typing import Any

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.dashboard_dto import WidgetDTO
from app.context.analytics.application.dto.mappers import (
    widget_config_from_dto,
    widget_position_merge,
    widget_size_merge,
    widget_to_dto,
)
from app.shared.domain.exceptions import ValidationException
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
    WidgetNotFoundException,
)
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_type import WidgetType


class UpdateWidgetCommand(BaseCommand):
    """Обновить виджет: title/query/size/position/display_params."""

    caller_id: str
    dashboard_id: str
    widget_id: str
    title: str | None = None
    query: AnalyticsQueryDTO | None = None
    size: dict[str, int] | None = None
    position: dict[str, int] | None = None
    display_params: dict[str, Any] | None = None


class UpdateWidgetHandler(BaseCommandHandler[UpdateWidgetCommand, WidgetDTO]):
    REQUIRED_PERMISSION = "analytics.write"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateWidgetCommand) -> WidgetDTO:
        dashboard = await self._repo.get_by_id(Id.from_string(command.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=command.dashboard_id)
        if dashboard.workspace_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
        elif str(dashboard.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)

        widget_id = Id.from_string(command.widget_id)
        widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
        if widget is None:
            raise WidgetNotFoundException(id=command.widget_id)

        new_config: WidgetConfig | None = None
        if command.query is not None:
            new_config = widget_config_from_dto(
                widget_type=widget.widget_type,
                query_dto=command.query,
                display_params=command.display_params
                if command.display_params is not None
                else (widget.config.display_params if widget.config else {}),
            )
        elif command.display_params is not None:
            if widget.config is None:
                # Нельзя задать display_params без query, если у виджета ещё
                # нет config — иначе VOконфига нечем заполнить.
                raise ValidationException(
                    field="display_params",
                    message="display_params нельзя обновить отдельно: у виджета ещё нет query",
                )
            new_config = WidgetConfig(
                widget_type=widget.config.widget_type,
                query=widget.config.query,
                display_params=command.display_params,
            )

        # Частичный update размера/позиции: мерджим с текущими значениями,
        # чтобы клиент мог передать только {"cols": 7} без перезаписи rows.
        new_size = widget_size_merge(widget.size, command.size)
        new_position = widget_position_merge(widget.position, command.position)

        dashboard.update_widget(
            widget_id=widget_id,
            title=command.title,
            config=new_config,
            size=new_size,
            position=new_position,
        )

        await self._repo.update(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
        updated = next(w for w in dashboard.widgets if w.id == widget_id)
        return widget_to_dto(updated)
