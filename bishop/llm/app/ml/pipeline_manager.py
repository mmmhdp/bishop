from app.common.logging_service import logger
from app.ml.llm.inference import process_inference_task
from app.ml.llm.train import process_train_task


def execute_task_pipeline(task_data):
    logger.info(f"Execute task with task_data: {task_data}")

    curr_event = task_data["event"]

    if curr_event == "health_check":
        logger.info("Executing health check pipeline")

    elif curr_event == "train_start":
        logger.info("Executing llm training pipeline")
        process_train_task(task_data)

    elif curr_event == "inference_response":
        logger.info("Executing llm inference pipeline")
        process_inference_task(task_data)
