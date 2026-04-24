from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.department_dto import DepartmentDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.aggregates.department import Department
from app.context.organization.domain.repositories.department_repository import DepartmentRepository


class CreateDepartmentCommand(BaseCommand):
    """
    Команда создания подразделения.

    Атрибуты:
        org_id: ID организации.
        name: Название подразделения.
        parent_id: ID родительского подразделения.
        lead_id: ID руководителя.
    """

    caller_id: str
    org_id: str
    name: str
    parent_id: str | None = None
    lead_id: str | None = None


class CreateDepartmentHandler(BaseCommandHandler[CreateDepartmentCommand, DepartmentDTO]):
    """
    Обработчик создания подразделения.

    Создаёт Department AR, сохраняет.
    """

    REQUIRED_PERMISSION = "departments.write"

    def __init__(self, department_repo: DepartmentRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._department_repo = department_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateDepartmentCommand) -> DepartmentDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        department = Department.create(
            org_id=Id.from_string(command.org_id),
            name=command.name,
            parent_id=Id.from_string(command.parent_id) if command.parent_id else None,
            lead_id=Id.from_string(command.lead_id) if command.lead_id else None,
        )

        await self._department_repo.add(department)
        await self._event_bus.publish_all(department.clear_domain_events())

        return DepartmentDTO(
            id=str(department.id),
            org_id=str(department.org_id),
            name=department.name,
            parent_id=str(department.parent_id) if department.parent_id else None,
            lead_id=str(department.lead_id) if department.lead_id else None,
            member_ids=[str(mid) for mid in department.member_ids],
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )
