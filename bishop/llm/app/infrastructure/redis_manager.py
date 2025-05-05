import redis
from typing import Optional
from app.common.config import settings
from app.common.logging_service import logger


class RedisManager:
    def __init__(self):
        """
        Initializes the RedisManager with a Redis client and key for tracking the running process ID.
        """
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.running_process_key = "ml:running_process_id"

    def set_running_process_id(self, pid: int) -> None:
        """
        Stores the given PID in Redis under the running_process_key.
        """
        self.redis_client.set(self.running_process_key, str(pid))
        logger.info(f"[RedisManager] Set running process ID: {pid}")

    def clear_running_process_id(self) -> None:
        """
        Removes the running process ID from Redis.
        """
        result = self.redis_client.delete(self.running_process_key)
        if result:
            logger.info("[RedisManager] Cleared running process ID from Redis.")
        else:
            logger.warning("[RedisManager] Tried to clear process ID, but key did not exist.")

    def get_running_process_id(self) -> Optional[int]:
        """
        Retrieves the currently stored running process ID from Redis.

        Returns:
            Optional[int]: Process ID if present, or None if no running process ID is found.
        """
        process_id = self.redis_client.get(self.running_process_key)
        if process_id is not None:
            logger.info(f"[RedisManager] Found running process ID: {process_id}")
            return int(process_id)
        else:
            logger.warning("[RedisManager] No running process ID found.")
            return None


redis_manager = RedisManager()
