from confluent_kafka import Consumer, KafkaError
import json
import time
from app.common.logging_service import logger
from app.ml.pipeline_manager import execute_task_pipeline


class KafkaMessageConsumer:
    def __init__(self, topics, bootstrap_servers, group_id, restart_delay=5):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # manually commit offsets
        }
        self.restart_delay = restart_delay

    def run(self):
        while True:
            consumer = Consumer(self.consumer_config)
            try:
                consumer.subscribe(self.topics)
                logger.info(f"Subscribed to topics: {self.topics}")

                while True:
                    msg = consumer.poll(1.0)

                    if msg is None:
                        continue

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            logger.info(
                                f"Reached end of partition for {msg.topic()}")
                        else:
                            logger.error(f"Kafka error: {msg.error()}")
                        continue

                    self.process_message(consumer, msg)

            except KeyboardInterrupt:
                logger.info("Consumer interrupted, shutting down...")
                break
            except Exception as e:
                logger.exception(f"Unexpected error: {e}. Restarting after {
                                 self.restart_delay} seconds...")
                time.sleep(self.restart_delay)
                logger.info("Restarting consumer...")
            finally:
                consumer.close()
                logger.info("Consumer closed.")

    def process_message(self, consumer, msg):
        try:
            task_data = json.loads(msg.value().decode('utf-8'))
            logger.info(f"Received task from {msg.topic()}: {task_data}")
            execute_task_pipeline(task_data)
            consumer.commit(msg)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            time.sleep(1)
