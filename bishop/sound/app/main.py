from app.broker.Consumer import KafkaMessageConsumer
from app.common.config import settings


def main():
    consumer = KafkaMessageConsumer(
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        topics=[
            settings.KAFKA_HEALTH_CHECK_TOPIC,
            settings.KAFKA_TOPIC_SOUND_TRAIN,
            settings.KAFKA_TOPIC_SOUND_INFERENCE,
        ],
        group_id=settings.KAFKA_GROUP_ID
    )
    consumer.run()


if __name__ == "__main__":
    main()
