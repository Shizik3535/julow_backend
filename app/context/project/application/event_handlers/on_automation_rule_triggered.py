from __future__ import annotations

import logging

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.repositories.board_repository import BoardRepository

logger = logging.getLogger(__name__)


class OnAutomationRuleTriggered(BaseEventHandler[BaseDomainEvent]):
    """
    Intra-BC event handler.

    Подписка на project.events — обрабатывает события,
    которые могут триггерить automation rules доски.
    Matching rules выполняют соответствующие actions.
    """

    def __init__(self, board_repo: BoardRepository) -> None:
        super().__init__()
        self._board_repo = board_repo

    async def handle(self, event: BaseDomainEvent) -> None:
        project_id_str = getattr(event, "project_id", None)
        if project_id_str is None:
            return

        board = await self._board_repo.get_by_project_id(Id.from_string(project_id_str))
        if board is None:
            return

        for rule in board.automation_rules:
            if not rule.is_enabled:
                continue

            if self._matches_trigger(event, rule):
                logger.info(
                    "Automation rule '%s' triggered by event %s for project %s",
                    rule.name,
                    type(event).__name__,
                    project_id_str,
                )

    @staticmethod
    def _matches_trigger(event: BaseDomainEvent, rule: object) -> bool:
        """Проверяет, совпадает ли триггер правила с событием."""
        trigger_value = getattr(rule, "trigger", None)
        if trigger_value is None:
            return False
        event_name = type(event).__name__.upper()
        trigger_name = str(trigger_value.value).upper() if hasattr(trigger_value, "value") else str(trigger_value).upper()
        return trigger_name in event_name
