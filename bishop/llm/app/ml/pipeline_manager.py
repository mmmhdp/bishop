from pathlib import Path

from app.broker.Producer import KafkaMessageProducer
from app.broker.producer_service import send_update_message_state
from app.common.config import settings
from app.common.logging_service import logger
from app.kaggle_api import kaggle_manager
from app.ml.data.dataset_utils import (
    download_data,
    convert_non_text_to_text,
    build_dataset,
)

producer = KafkaMessageProducer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
)


def execute_task_pipeline(task_data):
    logger.info(f"Execute task with task_data: {task_data}")

    curr_event = task_data["event"]

    if curr_event == "health_check":
        logger.info("Executing health check pipelines")

    elif curr_event == "train_start":
        logger.info("Executing train start pipelines")
        curr_event = task_data["event"]

        s3_urls = []
        for train_material in task_data["train_materials"]:
            s3_urls.append(train_material["url"])

        raw_data_local_paths = download_data(s3_urls)
        interim_data_local_paths = convert_non_text_to_text(raw_data_local_paths)
        dataset_path = build_dataset()

        if settings.IS_KAGGLE:
            kaggle_manager.authenticate()
            kaggle_manager.upload_dataset(dataset_path.parent)

            finetune_script_path = Path(settings.KAGGLE_FINETUNE_PATH)
            kernel_ref = kaggle_manager.run_script(finetune_script_path)
            kaggle_manager.track_execution(kernel_ref)

            kaggle_manager.download_output(kernel_ref, settings.MODEL_DIR)


    elif curr_event == "inference_response":
        logger.info("Executing inference pipelines")
        message_id = task_data["message_id"]
        text = task_data["text"]

        generated_text = "dummy_text"
        generated_dub_url = "app/sample.mp3"

        logger.info(f"Processing inference task with task_data: {task_data}")

        # generating logic call

        send_update_message_state(
            producer=producer,
            message_id=message_id,
            generated_text=generated_text,
            dub_url=generated_dub_url
        )
