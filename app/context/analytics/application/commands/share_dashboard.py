from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    InvalidShareAccessLevelException,
)
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel


class ShareDashboardCommand(BaseCommand):
    """Расшарить дашборд с пользователем."""

    caller_id: str
    dashboard_id: str
    user_id: str
    access_level: str = "view"  # ShareAccessLevel.value


class ShareDashboardHandler(BaseCommandHandler[ShareDashboardCommand, None]):
    REQUIRED_PERMISSION = "analytics.share"

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

    async def handle(self, command: ShareDashboardCommand) -> None:
        dashboard = await self._repo.get_by_id(Id.from_string(command.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=command.dashboard_id)
        if dashboard.workspace_id is not None:
            has_perm = await self._permission_checker.has_permission(
                user_id=command.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_perm and str(dashboard.owner_id) != command.caller_id:
                raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)
        elif str(dashboard.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)

        try:
            access_level = ShareAccessLevel(command.access_level)
        except ValueError as e:
            raise InvalidShareAccessLevelException(command.access_level) from e
        dashboard.share(
            user_id=Id.from_string(command.user_id),
            access_level=access_level,
        )
        await self._repo.update(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())


class UnshareDashboardCommand(BaseCommand):
    """Снять шаринг дашборда с пользователя."""

    caller_id: str
    dashboard_id: str
    user_id: str


class UnshareDashboardHandler(BaseCommandHandler[UnshareDashboardCommand, None]):
    REQUIRED_PERMISSION = "analytics.share"

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

    async def handle(self, command: UnshareDashboardCommand) -> None:
        dashboard = await self._repo.get_by_id(Id.from_string(command.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=command.dashboard_id)
        if dashboard.workspace_id is not None:
            has_perm = await self._permission_checker.has_permission(
                user_id=command.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_perm and str(dashboard.owner_id) != command.caller_id:
                raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)
        elif str(dashboard.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)

        dashboard.unshare(Id.from_string(command.user_id))
        await self._repo.update(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
