from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.repositories.department_repository import DepartmentRepository


class DeleteDepartmentCommand(BaseCommand):
    """
    Команда удаления (деактивации) подразделения.

    Атрибуты:
        department_id: ID подразделения.
    """

    caller_id: str
    org_id: str
    department_id: str


class DeleteDepartmentHandler(BaseCommandHandler[DeleteDepartmentCommand, None]):
    """
    Обработчик удаления подразделения.

    Загружает Department, вызывает deactivate, сохраняет.
    """

    REQUIRED_PERMISSION = "departments.write"

    def __init__(self, department_repo: DepartmentRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._department_repo = department_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeleteDepartmentCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        department = await self._department_repo.get_by_id(Id.from_string(command.department_id))
        if department is None:
            raise EntityNotFoundException(entity_type="Department", id=command.department_id)

        department.deactivate()
        await self._department_repo.update(department)
        await self._event_bus.publish_all(department.clear_domain_events())
