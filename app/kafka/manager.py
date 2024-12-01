from .producer import KafkaProducer
from datetime import datetime
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "rate_logs")


class KafkaManager:
    """Высокоуровневая обертка для логирования бизнес-событий в Kafka"""

    def __init__(self, kafka_server: str = KAFKA_SERVER, topic: str = KAFKA_TOPIC):
        self.kafka_server = kafka_server
        self.topic = topic
        self.producer = KafkaProducer(kafka_server=self.kafka_server)

    async def start(self):
        """Инициализация KafkaProducer"""
        await self.producer.start()

    async def stop(self):
        """Остановка KafkaProducer"""
        await self.producer.stop()

    async def log_action(self, action: str, user_id: int, rate_id: int, **kwargs):
        """Формирует сообщение и отправляет его в Kafka"""
        message = {
            "action": action,
            "user_id": user_id,
            "rate_id": rate_id,
            "timestamp": datetime.utcnow().isoformat(),  # Добавляем текущую метку времени
            "details": kwargs,
        }
        await self.producer.send_message(self.topic, message)
