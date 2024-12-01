import json
from aiokafka import AIOKafkaProducer


class KafkaProducer:
    """Низкоуровневый класс для работы с KafkaProducer"""

    def __init__(self, kafka_server: str):
        self.kafka_server = kafka_server
        self.producer = None  # Создание отложено до вызова start()

    async def start(self):
        """Инициализация AIOKafkaProducer в асинхронном контексте"""
        self.producer = AIOKafkaProducer(bootstrap_servers=self.kafka_server)
        await self.producer.start()

    async def stop(self):
        """Остановка AIOKafkaProducer"""
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, message: dict):
        """Отправляет сообщение в указанный топик"""
        if not self.producer:
            raise RuntimeError("Producer is not started. Call start() before using.")
        value = json.dumps(message).encode("utf-8")
        await self.producer.send_and_wait(topic, value)
