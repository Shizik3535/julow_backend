"""Интеграционные тесты KafkaMessageBrokerAdapter (реальный Kafka)."""

import asyncio
import json
import uuid
from typing import Any

import pytest
import pytest_asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.shared.infrastructure.messaging.kafka_message_broker_adapter import (
    KafkaMessageBrokerAdapter,
)


@pytest.mark.integration
class TestKafkaMessageBrokerAdapter:
    """Тесты Kafka-адаптера брокера сообщений."""

    @pytest_asyncio.fixture
    async def topic(self) -> str:
        return f"test-broker-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def adapter(self, kafka_producer: AIOKafkaProducer, kafka_bootstrap: str) -> KafkaMessageBrokerAdapter:
        return KafkaMessageBrokerAdapter(
            producer=kafka_producer,
            bootstrap_servers=kafka_bootstrap,
        )

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

    # ── publish ──────────────────────────────────────────────────────────

    async def test_publish_message(self, adapter: KafkaMessageBrokerAdapter, consumer, topic: str) -> None:
        message = {"event": "test_publish", "value": 42}
        await adapter.publish(topic, message)

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg.value)
                break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 1
        assert messages[0]["event"] == "test_publish"
        assert messages[0]["value"] == 42

    async def test_publish_with_key(self, adapter: KafkaMessageBrokerAdapter, consumer, topic: str) -> None:
        await adapter.publish(topic, {"keyed": True}, key="partition-key")

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg)
                break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 1
        assert messages[0].key == b"partition-key"
        assert messages[0].value["keyed"] is True

    async def test_publish_without_key(self, adapter: KafkaMessageBrokerAdapter, consumer, topic: str) -> None:
        await adapter.publish(topic, {"no_key": True})

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg)
                break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 1
        assert messages[0].key is None

    async def test_publish_unicode_message(self, adapter: KafkaMessageBrokerAdapter, consumer, topic: str) -> None:
        message = {"текст": "Привет, Kafka!", "emoji": "🚀"}
        await adapter.publish(topic, message)

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg.value)
                break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 1
        assert messages[0]["текст"] == "Привет, Kafka!"
        assert messages[0]["emoji"] == "🚀"

    async def test_publish_multiple_messages(self, adapter: KafkaMessageBrokerAdapter, consumer, topic: str) -> None:
        for i in range(3):
            await adapter.publish(topic, {"index": i})

        messages = []
        try:
            async for msg in consumer:
                messages.append(msg.value)
                if len(messages) >= 3:
                    break
        except asyncio.TimeoutError:
            pass

        assert len(messages) == 3
        indices = [m["index"] for m in messages]
        assert sorted(indices) == [0, 1, 2]

    # ── subscribe ────────────────────────────────────────────────────────

    async def test_subscribe_receives_messages(self, kafka_bootstrap: str) -> None:
        topic = f"test-sub-{uuid.uuid4().hex[:8]}"
        producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap)
        await producer.start()

        try:
            adapter = KafkaMessageBrokerAdapter(
                producer=producer,
                bootstrap_servers=kafka_bootstrap,
            )

            received: list[tuple[str, dict[str, Any]]] = []
            done = asyncio.Event()

            async def handler(t: str, data: dict[str, Any]) -> None:
                received.append((t, data))
                done.set()

            await adapter.subscribe(topic, group_id=f"sub-{uuid.uuid4().hex[:8]}", handler=handler)

            # Подождём, пока consumer стартует
            await asyncio.sleep(1)
            await adapter.publish(topic, {"subscribed": True})

            await asyncio.wait_for(done.wait(), timeout=10.0)

            assert len(received) == 1
            assert received[0][0] == topic
            assert received[0][1]["subscribed"] is True

        finally:
            await adapter.stop()

    # ── start / stop ─────────────────────────────────────────────────────

    async def test_start_and_stop_lifecycle(self, kafka_bootstrap: str) -> None:
        producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap)
        adapter = KafkaMessageBrokerAdapter(
            producer=producer,
            bootstrap_servers=kafka_bootstrap,
        )

        await adapter.start()

        topic = f"test-lifecycle-{uuid.uuid4().hex[:8]}"
        await adapter.publish(topic, {"lifecycle": True})

        await adapter.stop()

        assert len(adapter._consumers) == 0
        assert len(adapter._tasks) == 0

    async def test_stop_cleans_up_consumers_and_tasks(self, kafka_bootstrap: str) -> None:
        producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap)
        await producer.start()

        adapter = KafkaMessageBrokerAdapter(
            producer=producer,
            bootstrap_servers=kafka_bootstrap,
        )

        topic = f"test-cleanup-{uuid.uuid4().hex[:8]}"

        async def noop_handler(t: str, data: dict[str, Any]) -> None:
            pass

        await adapter.subscribe(topic, group_id="cleanup-test", handler=noop_handler)
        await asyncio.sleep(0.5)

        assert len(adapter._consumers) == 1
        assert len(adapter._tasks) == 1

        await adapter.stop()

        assert len(adapter._consumers) == 0
        assert len(adapter._tasks) == 0
