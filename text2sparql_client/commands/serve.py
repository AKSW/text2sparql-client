"""serve command"""

from asyncio import sleep

import click
import fastapi
import uvicorn
from pydantic_settings import BaseSettings

from text2sparql_client.context import ApplicationContext

SPARQL_ANSWER = """
SELECT ?resource
WHERE {
  ?resource a ?class .
}
LIMIT 1
"""

KNOWN_DATASETS = [
    "https://text2sparql.aksw.org/2025/dbpedia/",
    "https://text2sparql.aksw.org/2025/corporate/",
]


class Settings(BaseSettings):
    """Endpoint Settings"""

    sleep: int = 0


settings = Settings()

endpoint = fastapi.FastAPI(
    title="TEXT2SPARQL API Example",
)


def run_service(host: str, port: int) -> None:
    """Start uvicorn server"""
    uvicorn.run(endpoint, host=host, port=port)


@endpoint.get("/")
async def get_answer(question: str, dataset: str) -> dict[str, str]:
    """Serve some answers"""
    if dataset not in KNOWN_DATASETS:
        raise fastapi.HTTPException(404, "Unknown dataset ...")
    await sleep(settings.sleep)
    return {"dataset": dataset, "question": question, "query": SPARQL_ANSWER}


@click.command(name="serve")
@click.option(
    "--port",
    type=int,
    default=8000,
    show_default=True,
    help="The port to listen on.",
)
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    help="Bind socket to this host. "
    "Use '0.0.0.0' to make the endpoint available on your local network.",
)
@click.option(
    "--sleep",
    "sleep_",
    type=int,
    default=0,
    show_default=True,
    help="How long to sleep before answering.",
)
@click.pass_obj
def serve_command(app: ApplicationContext, port: int, host: str, sleep_: int) -> None:
    """Provide a TEXT2SPARQL testing endpoint

    This commands provides a simple noop endpoint for reference.
    """
    endpoint.debug = app.debug
    settings.sleep = sleep_
    run_service(host=host, port=port)
