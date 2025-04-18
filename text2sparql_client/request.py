"""TEXT2SPARQL Request"""

from datetime import UTC, datetime

from requests import get

from text2sparql_client.database import Database
from text2sparql_client.models.response import ResponseMessage


def text2sparql(
    endpoint: str, dataset: str, question: str, timeout: int, database: Database
) -> ResponseMessage:
    """Text to SPARQL Request."""
    timestamp = str(datetime.now(tz=UTC))
    database.register_question(
        time=timestamp,
        endpoint=endpoint,
        dataset=dataset,
        question=question,
    )
    try:
        response = get(
            url=endpoint,
            params={
                "dataset": dataset,
                "question": question,
            },
            timeout=timeout,
        )
        database.add_response(
            time=timestamp,
            endpoint=endpoint,
            dataset=dataset,
            question=question,
            response=response,
        )
    except Exception as error:
        database.add_exception(
            time=timestamp, endpoint=endpoint, dataset=dataset, question=question, exception=error
        )
        raise
    response_message = ResponseMessage(**response.json())
    response_message.endpoint = endpoint
    return response_message
