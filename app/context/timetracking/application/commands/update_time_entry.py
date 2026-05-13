from __future__ import annotations

from decimal import Decimal

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.money_vo import Money

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
from app.context.timetracking.application.exceptions.timetracking_app_exceptions import (
    TimeEntryHourlyRateRequiredException,
    TimeEntryNotOwnerException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.time_entry_exceptions import (
    TimeEntryNotFoundException,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class UpdateTimeEntryCommand(BaseCommand):
    """Команда обновления записи времени (только в DRAFT)."""

    caller_id: str
    entry_id: str
    description: str | None = None
    is_billable: bool | None = None
    hourly_rate_amount: str | None = None
    hourly_rate_currency: str | None = None
    category_id: str | None = None


class UpdateTimeEntryHandler(BaseCommandHandler[UpdateTimeEntryCommand, TimeEntryDTO]):
    """Обновление записи времени. Только владелец, только в DRAFT."""

    REQUIRED_PERMISSION = "time.write"

    def __init__(
        self,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = time_entry_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateTimeEntryCommand) -> TimeEntryDTO:
        entry = await self._repo.get_by_id(Id.from_string(command.entry_id))
        if entry is None:
            raise TimeEntryNotFoundException(id=command.entry_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(entry.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        if str(entry.user_id) != command.caller_id:
            raise TimeEntryNotOwnerException(command.entry_id)

        hourly_rate: Money | None = None
        rate_provided = (
            command.hourly_rate_amount is not None
            and command.hourly_rate_currency is not None
        )
        will_be_billable = (
            command.is_billable is True
            or (command.is_billable is None and entry.is_billable)
        )
        if command.is_billable is True and not rate_provided and entry.hourly_rate is None:
            # Включаем billable, но нет ставки — обязательна
            raise TimeEntryHourlyRateRequiredException()
        if rate_provided and will_be_billable:
            hourly_rate = Money(
                amount=Decimal(command.hourly_rate_amount),
                currency=command.hourly_rate_currency,
            )

        entry.update(
            description=command.description,
            is_billable=command.is_billable,
            hourly_rate=hourly_rate,
            category_id=Id.from_string(command.category_id) if command.category_id else None,
        )
        await self._repo.update(entry)
        await self._event_bus.publish_all(entry.clear_domain_events())
        return time_entry_to_dto(entry)
