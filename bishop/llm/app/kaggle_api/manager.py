import json
import time
from pathlib import Path
from typing import List

from kaggle import KaggleApi

from app.common.config import settings
from app.common.logging_service import logger
from app.kaggle_api.exceptions import KaggleAuthenticationError, KaggleManagerError


class KaggleManager:
    """Class for managing interactions with Kaggle API."""

    def __init__(self) -> None:
        """Initialize KaggleManager and KaggleApi instance."""
        self._api = KaggleApi()

    def authenticate(self) -> None:
        """Authenticate with the Kaggle API."""
        try:
            self._api.authenticate()
        except Exception as e:
            raise KaggleAuthenticationError("Failed to authenticate with Kaggle API") from e

    def upload_dataset(self, dataset_dir: Path) -> None:
        """Upload a dataset to Kaggle by creating a new version.

        Args:
            dataset_dir (Path): Path to the dataset directory.
        """
        dataset_config_path = self._generate_dataset_config(dataset_dir)

        try:
            self._api.dataset_create_version(
                folder=dataset_dir,
                version_notes="A universal version of the dataset for launching training",
            )
            logger.info(f"Dataset uploaded successfully from {dataset_dir}."
                        f"Waiting 7 seconds for Kaggle to update the data.")
            time.sleep(7)

            dataset_config_path.unlink(missing_ok=True)
            logger.info("Dataset metadata file deleted.")
        except Exception as e:
            raise KaggleManagerError(f"Failed to create a new version of the dataset from {dataset_dir}.") from e

    def run_script(self, py_script_path: Path) -> str:
        """Upload and run a Python script on Kaggle.

        Args:
            py_script_path (Path): Path to the Python script.

        Returns:
            str: Reference of the created Kaggle kernel.
        """
        self.__generate_py_script_config(py_script_path)

        try:
            logger.info(f"Uploading python script {py_script_path} to Kaggle...")
            response = self._api.kernels_push(
                folder=py_script_path.parent,
                timeout=settings.KAGGLE_KERNEL_RUN_TIMEOUT,
            )
            logger.info(f"Python script {py_script_path} uploaded successfully.")

            py_script_path.unlink(missing_ok=True)
            logger.info(f"Kernel metadata deleted.")

            kernel_ref = f"{settings.KAGGLE_AUTH_NAME}/{settings.KAGGLE_KERNEL_TITLE}"
            return kernel_ref
        except Exception as e:
            raise KaggleManagerError(f"Failed to upload python script {py_script_path} to Kaggle.") from e

    def track_execution(self, kernel_ref: str) -> None:
        """Track the execution status of a Kaggle kernel.

        Args:
            kernel_ref (str): Kernel reference ID.
        """
        while True:
            status_response = self._api.kernels_status(kernel_ref)
            status = status_response.status.name

            if status == "COMPLETE":
                logger.info(f"Kernel '{kernel_ref}' completed successfully.")
                return
            elif status in (
                    "ERROR",
                    "CANCEL_REQUESTED",
                    "CANCEL_ACKNOWLEDGED",
            ):
                error_msg = f"Kernel '{kernel_ref}' failed with status: {status}"
                if failure_message := status_response.failure_message:
                    error_msg += f" | Message: {failure_message}"
                raise RuntimeError(error_msg)
            elif status == "QUEUED":
                logger.info(f"Kernel '{kernel_ref}' is in queue...")
                time.sleep(5)
            elif status in (
                    "RUNNING",
                    "NEW_SCRIPT"
            ):
                logger.info(f"Kernel '{kernel_ref}' is in progress...")
                time.sleep(3)

    def download_output(self, kernel_ref: str, output_dir: Path) -> List[Path]:
        """Download output files of a Kaggle kernel.

        Args:
            kernel_ref (str): Kernel reference ID.
            output_dir (Path): Directory where outputs will be saved.

        Returns:
            List[Path]: List of downloaded file paths.
        """
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if not output_dir.is_dir():
            raise ValueError("Provided path must be a directory.")

        try:
            logger.info(f"Downloading output of kernel '{kernel_ref}' to '{output_dir}'...")
            outfiles, token = self._api.kernels_output(
                kernel=kernel_ref,
                path=output_dir,
                force=True
            )
            logger.info(f"Downloading output of kernel '{kernel_ref}' to '{output_dir}' completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to download output for kernel '{kernel_ref}'") from e

        if not outfiles:
            logger.warning(f"No output files found for kernel '{kernel_ref}'")
        else:
            logger.info(f"Downloaded {len(outfiles)} files from kernel '{kernel_ref}'")

        return [Path(f) for f in outfiles]

    def __generate_py_script_config(self, py_script_path: Path) -> None:
        """Generate kernel-metadata.json for a Python script.

        Args:
            py_script_path (Path): Path to the Python script.
        """
        if not py_script_path.is_file():
            raise ValueError(f"Provided python script path {py_script_path} is not a valid file.")

        kernel_metadata_file = py_script_path.parent / "kernel-metadata.json"

        dataset_ref = f"{settings.KAGGLE_AUTH_NAME}/{settings.KAGGLE_DATASET_TITLE}"

        kernel_metadata = {
            "id": f"{settings.KAGGLE_AUTH_NAME}/{settings.KAGGLE_KERNEL_TITLE}",
            "title": settings.KAGGLE_KERNEL_TITLE.replace("-", " ").capitalize(),
            "code_file": py_script_path.name,
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": True,
            "enable_tpu": False,
            "enable_internet": True,
            "dataset_sources": [dataset_ref],
            "competition_sources": [],
            "kernel_sources": [],
            "model_sources": [],
        }

        with open(kernel_metadata_file, 'w') as f:
            json.dump(kernel_metadata, f, indent=4)

        logger.info(f"Kernel metadata created at {py_script_path}")

    def _generate_dataset_config(self, dataset_dir: Path) -> Path:
        """Generate dataset-metadata.json for a dataset directory.

        Args:
            dataset_dir (Path): Path to the dataset directory.

        Returns:
            Path: Dataset metadata file path.
        """
        if not dataset_dir.is_dir():
            raise ValueError(f"Provided dataset folder path {dataset_dir} is not a valid directory.")

        dataset_metadata_file = dataset_dir / "dataset-metadata.json"

        dataset_metadata = {
            "id": f"{settings.KAGGLE_AUTH_NAME}/{settings.KAGGLE_DATASET_TITLE}",
            "title": settings.KAGGLE_DATASET_TITLE.replace("-", " ").capitalize(),
            "licenses": [{"name": "CC0-1.0"}],
            "is_public": False,
        }

        with open(dataset_metadata_file, 'w') as f:
            json.dump(dataset_metadata, f, indent=4)

        logger.info(f"Dataset metadata created at {dataset_metadata_file}")

        return dataset_metadata_file


kaggle_manager = KaggleManager()
