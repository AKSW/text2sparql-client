"""TEXT2SPARQL Request"""

from datetime import UTC, datetime

from requests import Response, get

from text2sparql_client.database import Database
from text2sparql_client.models.response import ResponseMessage


def response_to_response_message(endpoint: str, response: Response) -> ResponseMessage:
    """Create a response message"""
    response_message = ResponseMessage(**response.json())
    response_message.endpoint = endpoint
    return response_message


def text2sparql(  # noqa: PLR0913
    endpoint: str, dataset: str, question: str, timeout: int, database: Database, cache: bool
) -> ResponseMessage:
    """Text to SPARQL Request."""
    if cache and (
        cached_response := database.get_response(
            endpoint=endpoint, dataset=dataset, question=question
        )
    ):
        return response_to_response_message(endpoint=endpoint, response=cached_response)

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
    return response_to_response_message(endpoint=endpoint, response=response)
