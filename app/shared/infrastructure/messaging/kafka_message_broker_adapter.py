from __future__ import annotations

import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.logging import get_logger
from app.shared.application.ports.messaging.message_broker_port import (
    MessageBrokerPort,
    MessageHandler,
)

logger = get_logger(__name__)


class KafkaMessageBrokerAdapter(MessageBrokerPort):
    """
    Реализация MessageBrokerPort на основе aiokafka.

    Поддерживает публикацию в топики, подписку с consumer groups,
    lifecycle-управление (start/stop).

    Аргументы конструктора:
        producer: AIOKafkaProducer для публикации сообщений.
        bootstrap_servers: Адреса Kafka брокеров.
        auto_offset_reset: Стратегия смещения (earliest, latest).
    """

    def __init__(
        self,
        producer: AIOKafkaProducer,
        bootstrap_servers: str,
        auto_offset_reset: str = "earliest",
    ) -> None:
        self._producer = producer
        self._bootstrap_servers = bootstrap_servers
        self._auto_offset_reset = auto_offset_reset
        self._consumers: dict[str, AIOKafkaConsumer] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def publish(self, topic: str, message: dict[str, Any], key: str | None = None) -> None:
        serialized = json.dumps(message, default=str, ensure_ascii=False).encode("utf-8")
        key_bytes = key.encode("utf-8") if key else None
        await self._producer.send_and_wait(topic, serialized, key=key_bytes)
        logger.debug("Message published", topic=topic, key=key)

    async def subscribe(self, topic: str, group_id: str, handler: MessageHandler) -> None:
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset=self._auto_offset_reset,
        )
        self._consumers[topic] = consumer
        await consumer.start()
        logger.info("Subscribed to topic", topic=topic, group_id=group_id)

        async def _consume() -> None:
            try:
                async for record in consumer:
                    try:
                        await handler(record.topic, record.value)
                    except Exception as e:
                        logger.error(
                            "Message handler error",
                            topic=record.topic,
                            error=str(e),
                        )
            except asyncio.CancelledError:
                pass

        self._tasks[topic] = asyncio.create_task(_consume())

    async def start(self) -> None:
        await self._producer.start()
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        # 1. Cancel consume tasks and wait for them to finish
        for task in self._tasks.values():
            task.cancel()
        for task in self._tasks.values():
            try:
                await task
            except asyncio.CancelledError:
                pass

        # 2. Stop consumers
        for consumer in self._consumers.values():
            await consumer.stop()

        # 3. Stop producer
        await self._producer.stop()

        self._consumers.clear()
        self._tasks.clear()
        logger.info("Kafka adapter stopped")
