"""TEXT2SPARQL Request"""

from datetime import UTC, datetime

from pydantic import BaseModel
from requests import get

from text2sparql_client.sqlite import Database


class ResponseMessage(BaseModel):
    """Endpoint Response (pydantic model)"""

    dataset: str
    question: str
    query: str
    endpoint: str | None = None


def text2sparql(
    endpoint: str, dataset: str, question: str, timeout: int, database: Database
) -> ResponseMessage:
    """Text to SPARQL Request."""
    response = get(
        url=endpoint,
        params={
            "dataset": dataset,
            "question": question,
        },
        timeout=timeout,
    )
    database.add_response(
        time=str(datetime.now(tz=UTC)),
        endpoint=endpoint,
        dataset=dataset,
        question=question,
        response=response,
    )
    response_message = ResponseMessage(**response.json())
    response_message.endpoint = endpoint
    return response_message
