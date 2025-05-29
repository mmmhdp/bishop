from confluent_kafka import Producer
import json
from app.common.logging_service import logger


class KafkaMessageProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = Producer(self.producer_config)

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{
                        msg.partition()}] at offset {msg.offset()}")

    def send(self, topic, data: dict):
        try:
            message = json.dumps(data).encode('utf-8')
            kwargs = dict(
                topic=topic,
                value=message,
                callback=self.delivery_report
            )
            self.producer.produce(**kwargs)
            self.producer.poll(0)
        except Exception as e:
            logger.exception(f"Failed to send message to topic '{topic}': {e}")

    def flush(self):
        self.producer.flush
