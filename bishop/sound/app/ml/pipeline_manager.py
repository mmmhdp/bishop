from app.common.logging_service import logger
from app.ml.audio.inference_dub import process_inference_task


def execute_task_pipeline(task_data):
    logger.info(f"Execute task with task_data: {task_data}")

    curr_event = task_data["event"]

    if curr_event == "health_check":
        logger.info("Executing health check pipeline for sound")

    elif curr_event == "sound_inference":
        logger.info("Executing sound inference pipeline")
        process_inference_task(task_data)
