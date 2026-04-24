"""Интеграционные тесты BrokerDomainEventBus (реальный Kafka)."""

import asyncio
import json
import uuid

import pytest
import pytest_asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.base_domain_event import BaseDomainEvent
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestBrokerDomainEventBus:
    """Тесты публикации доменных событий через Kafka."""

    @pytest_asyncio.fixture
    async def topic(self) -> str:
        return f"test-events-{uuid.uuid4().hex[:8]}"

    @pytest_asyncio.fixture
    async def event_bus(self, kafka_producer: AIOKafkaProducer, topic: str) -> BrokerDomainEventBus:
        from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort
        from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter

        broker = KafkaMessageBrokerAdapter(
            producer=kafka_producer,
            bootstrap_servers="",  # не используется для publish
        )
        return BrokerDomainEventBus(broker=broker, topic=topic)

    @pytest_asyncio.fixture
    async def consumer(self, kafka_bootstrap: str, topic: str):
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_bootstrap,
            group_id=f"test-group-{uuid.uuid4().hex[:8]}",
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            consumer_timeout_ms=5000,
        )
        await consumer.start()
        yield consumer
        await consumer.stop()

    async def test_publish_single_event(self, event_bus, consumer, topic) -> None:
        event = BaseDomainEvent(
            aggregate_id=Id.generate(),
            aggregate_type="TestAggregate",
        )
        await event_bus.publish_all([event])

        # Дождёмся получения сообщения
        messages = []
        try:
            async for msg in consumer:
                messages.append(msg.value)
                break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 1
        envelope = messages[0]
        assert envelope["event_type"] == "BaseDomainEvent"
        assert "event_id" in envelope
        assert "occurred_at" in envelope
        assert "payload" in envelope

    async def test_publish_multiple_events(self, event_bus, consumer, topic) -> None:
        events = [
            BaseDomainEvent(aggregate_id=Id.generate(), aggregate_type="A"),
            BaseDomainEvent(aggregate_id=Id.generate(), aggregate_type="B"),
        ]
        await event_bus.publish_all(events)

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg.value)
                if len(messages) >= 2:
                    break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 2

    async def test_publish_empty_list_no_error(self, event_bus) -> None:
        await event_bus.publish_all([])
