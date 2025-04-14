"""query command"""

import json
from io import TextIOWrapper
from pathlib import Path

import click
import requests
import yaml
from pydantic import BaseModel

from text2sparql_client.context import ApplicationContext
from text2sparql_client.request import text2sparql
from text2sparql_client.sqlite import Database


class Question(BaseModel):
    """Question (pydantic model)"""

    question: dict[str, str]


class DatasetDescription(BaseModel):
    """Dataset (pydantic model)"""

    id: str


class QuestionsFile(BaseModel):
    """Questions File (pydantic model)"""

    dataset: DatasetDescription
    questions: list[Question]


@click.command(name="ask")
@click.argument("QUESTIONS_FILE", type=click.File())
@click.argument("URL", type=click.STRING)
@click.option(
    "--answers-db",
    default="responses.db",
    type=click.Path(writable=True, readable=True, dir_okay=False),
    show_default=True,
    help="Where to save the endpoint responses.",
)
@click.option(
    "--timeout",
    type=int,
    default=120,
    show_default=True,
    help="Timeout in seconds.",
)
@click.pass_obj
def ask_command(
    app: ApplicationContext,
    questions_file: TextIOWrapper,
    url: str,
    answers_db: str,
    timeout: int,
) -> None:
    """Query a TEXT2SPARQL endpoint

    Use a questions YAML file and send each question to a TEXT2SPARQL conform endpoint.
    This command will create a sqlite database (--answers-db) saving the responses.
    """
    database = Database(file=Path(answers_db))
    file_model = QuestionsFile.model_validate(yaml.safe_load(questions_file))
    app.echo_info(f"Asking questions about dataset {file_model.dataset.id} on endpoint {url}.")
    responses = []
    for questions in file_model.questions:
        for language, question in questions.question.items():
            app.echo_info(f"{question} ({language}) ... ", nl=False)
            try:
                response = text2sparql(
                    endpoint=url,
                    dataset=file_model.dataset.id,
                    question=question,
                    database=database,
                    timeout=timeout,
                )
                app.echo_info("done", fg="green")
                responses.append(response.model_dump())
            except (requests.ConnectionError, requests.HTTPError, requests.ReadTimeout) as error:
                app.echo_info(str(error), fg="red")
    click.secho(json.dumps(responses, indent=2))
