import secrets
import warnings
from typing import Literal, Optional, List

from pydantic import HttpUrl, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Basic configuration
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SERVICE_NAME: str = "ml-service"

    # Kafka Configuration
    KAFKA_BROKER_URL: str
    KAFKA_GROUP_ID: str = "llm"
    KAFKA_TOPIC_LLM_INFERENCE: str = "llm-inference"
    KAFKA_TOPIC_LLM_TRAIN: str = "llm-train"
    KAFKA_TOPIC_SAVE_RESPONSE: str = "save-response"
    KAFKA_LLM_HEALTH_CHECK_TOPIC: str = "health-check-llm"

    # Add a list of complex topics
    KAFKA_COMPLEX_TOPICS: List = [
        KAFKA_TOPIC_LLM_INFERENCE,
        KAFKA_TOPIC_LLM_TRAIN,
    ]

    # MinIO (S3-compatible storage) Configuration
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_USE_SSL: bool = False
    MINIO_CACHE_DIR: str = "app/ml/data/raw"

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    # Secret for internal use (e.g., signing payloads)
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Kaggle API Configuration
    IS_KAGGLE: bool = True
    KAGGLE_AUTH_NAME: str = "atsamaz"
    KAGGLE_DATASET_TITLE: str = "avatar-finetuning-dataset"
    KAGGLE_KERNEL_TITLE: str = "avatar-finetuning"
    KAGGLE_KERNEL_RUN_TIMEOUT: int = 12600
    KAGGLE_FINETUNE_PATH: str = "app/ml/modeling/kaggle_finetune.py"

    # Data processing configuration
    PROCESSED_DATA_DIR: str = "app/ml/data/processed"
    RAW_DATA_DIR: str = MINIO_CACHE_DIR
    INTERIM_DATA_DIR: str = "app/ml/data/interim"
    MODEL_DIR: str = "app/ml/models"

    @computed_field
    @property
    def MINIO_URL(self) -> str:
        scheme = "https" if self.MINIO_USE_SSL else "http"
        return f"{scheme}://{self.MINIO_ENDPOINT}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Security validations
    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("MINIO_SECRET_KEY", self.MINIO_SECRET_KEY)

        return self


settings = Settings()
