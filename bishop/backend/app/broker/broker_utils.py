# from urllib.parse import urlparse
# from app.common.logging_service import logger
#
#
# def get_object_key_from_url(url: str, bucket_name: str) -> str:
#    if isinstance(url, bytes):
#        url = url.decode('utf-8')
#    parsed = urlparse(url)
#    path = parsed.path.lstrip("/")
#    if path.startswith(bucket_name + "/"):
#        return path[len(bucket_name) + 1:]
#    raise ValueError("URL does not contain expected bucket prefix")

from urllib.parse import urlparse
from app.common.logging_service import logger


def get_object_key_from_url(url: str, bucket_name: str) -> str:
    if url is None or url == "":
        logger.error(
            f"[get_object_key_from_url] URL is None or empty. Bucket name: {bucket_name}")
        return None
    logger.debug(f"[get_object_key_from_url] Called with url={
                 repr(url)}, bucket_name={repr(bucket_name)}")
    original_type = type(url)
    logger.debug(f"[get_object_key_from_url] Type of url: {original_type}")

    if isinstance(url, bytes):
        try:
            url = url.decode('utf-8')
            logger.debug(
                f"[get_object_key_from_url] Decoded bytes url to str: {url}")
        except Exception as decode_exc:
            logger.error(
                f"[get_object_key_from_url] Failed to decode bytes url: {decode_exc}")
            raise

    parsed = urlparse(url)
    logger.debug(f"[get_object_key_from_url] Parsed URL: {parsed}")
    logger.debug(f"[get_object_key_from_url] Parsed path: {parsed.path}")

    path = parsed.path.lstrip("/")
    logger.debug(f"[get_object_key_from_url] Stripped leading slash: {path}")

    prefix = bucket_name + "/"
    if path.startswith(prefix):
        object_key = path[len(prefix):]
        logger.debug(
            f"[get_object_key_from_url] Stripped bucket prefix: {object_key}")
        return object_key
    else:
        logger.error(f"[get_object_key_from_url] URL path '{
                     path}' does not start with expected bucket prefix '{prefix}'. Full URL: {url}")
        raise ValueError(f"URL does not contain expected bucket prefix '{
                         bucket_name}'. Path: {path}, Full URL: {url}")
