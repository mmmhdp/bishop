from httpx import AsyncClient
from app.common.config import settings
import random
import string


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_superuser_token_headers_async(client: AsyncClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

