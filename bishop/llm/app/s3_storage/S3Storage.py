from app.common.db import minio_client
from app.common.config import settings
from urllib.parse import urlparse
from minio.error import S3Error
from app.common.logging_service import logger
from typing import Optional, Union
from pathlib import Path



class S3StorageWithCache:
    def __init__(
        self,
        cache_dir: Path,
    ):
        self.client = minio_client
        self.bucket_name = settings.MINIO_BUCKET
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_obj_key_from_url(self, s3_url: str) -> str:
        """
        Convert S3 url to object key

        Example:
            http://ENDPOINT/BUCKET_NAME/root_dir/child_dir/file.txt ->
            ->                          root_dir/child_dir/file.txt
        """
        parsed = urlparse(s3_url)
        path = parsed.path.lstrip("/")
        if path.startswith(self.bucket_name + "/"):
            return path[len(self.bucket_name) + 1:]
        raise ValueError("URL does not contain expected bucket prefix")

    def _url_to_cache_path_and_obj_key(self, s3_url: str) -> tuple[Path, str]:
        """
        Convert S3 url to cache path and object key

        Example:
            s3_url = "http://ENDPOINT/BUCKET_NAME/root_dir/child_dir/file.txt"
            cache path = ./{self.cache_dir}/root_dir/child_dir/file.txt"
            object_key = "root_dir/child_dir/file.txt"
        """

        object_key = self._get_obj_key_from_url(s3_url)
        return self.cache_dir / object_key, object_key

    def download_file(self, s3_url: str) -> Path:
        """Download file from S3 to cache_dir if file is still not in cache"""
        cache_path, object_key = self._url_to_cache_path_and_obj_key(s3_url)
        
        if cache_path.exists():
            logger.info(f"File {s3_url} already in cache at {cache_path}")
            return cache_path

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.client.fget_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            file_path=str(cache_path),
        )
        logger.info(f"Downloaded {s3_url} -> {cache_path}")
        return cache_path

    def upload_file(self, local_path: Path, object_key: str):
        """
        Upload local file from local_path to S3 and allocate it with object key
        
        Example:
            local_path = "./storage/data/file.txt"
            object_key = "user1/text/file.txt"
            will be uploaded to S3
            s3_url = "http://ENDPOINT/BUCKET_NAME/user1/text/file.txt"
        """
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            file_path=str(local_path),
        )

        logger.info(f"Uploaded file {local_path}, with object_key {object_key}")

    def delete_file(self, s3_url: str):
        """Remove object from S3"""

        _, object_key = self._url_to_cache_path_and_obj_key(s3_url)

        self.client.remove_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
        )
        logger.info(f"Deleted {s3_url} from S3")


s3_storage = S3StorageWithCache(cache_dir=Path(settings.MINIO_CACHE_DIR))
