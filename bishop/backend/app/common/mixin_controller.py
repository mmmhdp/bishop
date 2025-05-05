from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.common.api_deps import get_current_active_superuser
from app.common.models.SimpleMessage import SimpleMessage
from app.email.email_service import generate_test_email, send_email
from app.common.api_deps import ProducerDep

router = APIRouter()


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
async def test_email(email_to: EmailStr) -> SimpleMessage:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return SimpleMessage(message="Test email sent")


@router.get("/health-check/")
async def health_check(producer: ProducerDep) -> bool:
    # await producer.send(
    #    topic="health-check-llm", data={
    #        "event": "health-check",
    #        "status": "ok"
    #    })
    # await producer.send(
    #    topic="health-check-sound", data={
    #        "status": "ok",
    #        "event": "health-check",
    #    })
    # await producer.flush()
    return True
