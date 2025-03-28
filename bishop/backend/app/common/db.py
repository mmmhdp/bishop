from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from app.user import user_repository
from app.common.config import settings
from app.user.User import User, UserCreate
import app.common.models_init


from minio import Minio
from redis import asyncio as AsyncRedis

redis_client = AsyncRedis.from_url(
    url=settings.REDIS_URL,
    decode_responses=True
)


minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL,
)

async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))


async def init_db(session: AsyncSession) -> None:

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    search_result = await session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = search_result.first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await user_repository.create_user(session=session, user_create=user_in)

    if not minio_client.bucket_exists(settings.MINIO_BUCKET):
        minio_client.make_bucket(settings.MINIO_BUCKET)
