from app.common.logging_service import logger


def process_train_task(task_data):
    curr_event = task_data["event"]

    if curr_event == "health_check":
        logger.info("Executing health check pipeline for llm")
