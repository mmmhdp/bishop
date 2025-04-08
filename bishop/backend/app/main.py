import asyncio
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.common.config import settings
from app.common.logging_service import logger
from app.broker.Producer import KafkaMessageProducer
from app.message.MessageManagerConsumer import MessageManagerConsumer


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


producer = KafkaMessageProducer(bootstrap_servers=settings.KAFKA_BROKER_URL)
message_manager_consumer = MessageManagerConsumer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
    topics=[
        settings.KAFKA_TOPIC_SAVE_RESPONSE,
    ],
    group_id=settings.KAFKA_GROUP_ID
)


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    await producer.start()
    app.state.producer = producer
    logger.info(f"Kafka producer started with bootstrap servers: {
                settings.KAFKA_BROKER_URL}")
    app.state.message_consumer_task = asyncio.create_task(
        message_manager_consumer.start())
    app.state.message_manager_consumer = message_manager_consumer


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    await producer.flush()
    await producer.stop()

    await message_manager_consumer.stop()

    task = app.state.message_consumer_task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled.")
