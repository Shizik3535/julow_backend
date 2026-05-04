from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import Any

from app.core.logging import get_logger
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort
from app.shared.domain.base_domain_event import BaseDomainEvent

logger = get_logger(__name__)


class BrokerDomainEventBus(DomainEventBus):
    """
    Реализация DomainEventBus поверх MessageBrokerPort.

    Экземпляр привязан к одному топику BC. Для каждого события
    формируется envelope ``{event_type, event_id, occurred_at, payload}``
    и публикуется в брокер. Если у события есть ``user_id``, оно
    используется как ключ партиционирования.

    Аргументы конструктора:
        broker: Порт брокера сообщений.
        topic: Имя топика BC (например ``"identity.events"``).
    """

    def __init__(self, broker: MessageBrokerPort, topic: str) -> None:
        self._broker = broker
        self._topic = topic

    @staticmethod
    def _convert_enums(obj: Any) -> Any:
        """Рекурсивно конвертирует Enum-значения в строки для JSON-сериализации."""
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, dict):
            return {k: BrokerDomainEventBus._convert_enums(v) for k, v in obj.items()}
        if isinstance(obj, list | tuple):
            return [BrokerDomainEventBus._convert_enums(v) for v in obj]
        return obj

    async def publish_all(self, events: list[BaseDomainEvent]) -> None:
        for event in events:
            event_type = type(event).__name__
            payload = BrokerDomainEventBus._convert_enums(asdict(event))
            message: dict[str, Any] = {
                "event_type": event_type,
                "event_id": str(event.event_id),
                "occurred_at": event.occurred_at.isoformat(),
                "payload": payload,
            }
            key = str(getattr(event, "user_id")) if hasattr(event, "user_id") else None

            await self._broker.publish(topic=self._topic, message=message, key=key)

            logger.info(
                "Domain event published",
                event_type=event_type,
                topic=self._topic,
            )
