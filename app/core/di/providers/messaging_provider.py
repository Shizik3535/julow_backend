from aiokafka import AIOKafkaProducer

from app.core.config.kafka_settings import KafkaSettings
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


def create_kafka_producer(settings: KafkaSettings) -> AIOKafkaProducer:
    """Создать AIOKafkaProducer."""
    return AIOKafkaProducer(bootstrap_servers=settings.bootstrap_servers)
