"""response message"""

from pydantic import BaseModel


class ResponseMessage(BaseModel):
    """Endpoint Response (pydantic model)"""

    dataset: str
    question: str
    query: str
    endpoint: str | None = None
