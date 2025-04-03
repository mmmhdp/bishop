from urllib.parse import urlparse


def get_object_key_from_url(url: str, bucket_name: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")
    if path.startswith(bucket_name + "/"):
        return path[len(bucket_name) + 1:]
    raise ValueError("URL does not contain expected bucket prefix")
