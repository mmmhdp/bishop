from sqlmodel import SQLModel


class SimpleMessage(SQLModel):
    message: str
