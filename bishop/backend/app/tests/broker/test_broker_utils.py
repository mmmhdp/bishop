import pytest
from app.broker.broker_utils import get_object_key_from_url


def test_valid_url():
    url = "http://s3:9000/app/users/52476a7c-2541-41fe-8dcb-f52c03159e61/avatars/1234/text/file.txt"
    bucket_name = "app"
    expected_key = "users/52476a7c-2541-41fe-8dcb-f52c03159e61/avatars/1234/text/file.txt"
    assert get_object_key_from_url(url, bucket_name) == expected_key


def test_url_with_trailing_slash():
    url = "http://s3:9000/app/users/1234/"
    bucket_name = "app"
    expected_key = "users/1234/"
    assert get_object_key_from_url(url, bucket_name) == expected_key


def test_url_without_bucket_prefix():
    url = "http://s3:9000/otherbucket/users/1234/file.txt"
    bucket_name = "app"
    with pytest.raises(ValueError, match="URL does not contain expected bucket prefix"):
        get_object_key_from_url(url, bucket_name)


def test_url_with_similar_prefix():
    url = "http://s3:9000/application/users/1234/file.txt"
    bucket_name = "app"
    with pytest.raises(ValueError):
        get_object_key_from_url(url, bucket_name)


def test_url_exact_bucket_only():
    url = "http://s3:9000/app/"
    bucket_name = "app"
    expected_key = ""
    assert get_object_key_from_url(url, bucket_name) == expected_key
