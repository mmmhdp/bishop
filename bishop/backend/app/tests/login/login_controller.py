from unittest.mock import patch

from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest

from app.common.config import settings
from app.security.security_service import verify_password
from app.user.User import User
from app.security.security_service import generate_password_reset_token


@pytest.mark.asyncio
async def test_get_access_token(async_client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await async_client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


@pytest.mark.asyncio
async def test_get_access_token_incorrect_password(async_client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = await async_client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_use_access_token(
    async_client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await async_client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


@pytest.mark.asyncio
async def test_recovery_password(
    async_client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.common.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.common.config.settings.SMTP_USER", "admin@example.com"),
    ):
        email = "test@example.com"
        r = await async_client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_recovery_password_user_not_exits(
    async_client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    email = "jVgQr@example.com"
    r = await async_client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_reset_password(
    async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    token = generate_password_reset_token(email=settings.FIRST_SUPERUSER)
    data = {"new_password": "changethis", "token": token}
    r = await async_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await db.exec(user_query)
    user = user_result.first()
    assert user
    assert verify_password(data["new_password"], user.hashed_password)


@pytest.mark.asyncio
async def test_reset_password_invalid_token(
    async_client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = await async_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"
