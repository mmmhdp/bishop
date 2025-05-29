import os
from multiprocessing import Process
import signal
from app.common.logging_service import logger
from app.infrastructure import redis_manager


def is_process_running() -> bool:
    """
    Checks if a process is already running based on the value in Redis.

    Returns:
        bool: True if a process is running, otherwise False.
    """
    process_id = redis_manager.get_running_process_id()
    if process_id:
        logger.info(f"Process with PID {process_id} is already running.")
        return True
    return False


def run_task_in_process(func, *args):
    """
    Starts the given function in a separate process if no other process is currently running.

    Args:
        func (callable): The function to run in a separate process.
        *args: Arguments to pass to the function.
    """
    if is_process_running():
        logger.warning("A process is already running. Rejecting new request.")
        return

    logger.info("Launching task in a separate process")
    p = Process(target=func, args=args)
    p.start()

    redis_manager.set_running_process_id(p.pid)
    logger.info(f"Started task with PID {p.pid}")


def terminate_process(pid: int) -> bool:
    """
    Terminates the process with the given PID.

    Args:
        pid (int): The process ID to terminate.

    Returns:
        bool: True if the termination was successful, otherwise False.
    """
    try:
        os.kill(pid, signal.SIGTERM)
        logger.info(
            f"Successfully sent termination signal to process with PID {pid}")
        return True
    except ProcessLookupError:
        logger.warning(f"Process with PID {pid} not found.")
        return False
    except Exception as e:
        logger.error(f"Error while trying to terminate process {pid}: {e}")
        return False


def is_process_alive() -> bool:
    """
    Checks if the active process is alive based on the PID stored in Redis.

    Returns:
        bool: True if the process is alive, otherwise False.
    """
    pid = redis_manager.get_running_process_id()
    if not pid:
        logger.warning("No active process found.")
        return False

    try:
        os.kill(pid, 0)
        logger.info(f"Process with PID {pid} is alive.")
        return True
    except ProcessLookupError:
        logger.warning(f"Process with PID {pid} is not alive.")
        redis_manager.clear_running_process_id()
        return False
    except Exception as e:
        logger.error(f"Error while checking process {pid}: {e}")
        return False
