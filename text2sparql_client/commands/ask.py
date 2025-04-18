"""query command"""

import json
from io import TextIOWrapper
from pathlib import Path

import click
import requests
import yaml
from loguru import logger
from pydantic import ValidationError

from text2sparql_client.database import Database
from text2sparql_client.models.questions_file import QuestionsFile
from text2sparql_client.request import text2sparql


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
def ask_command(
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
    logger.info(f"Asking questions about dataset {file_model.dataset.id} on endpoint {url}.")
    responses = []
    for question_section in file_model.questions:
        for language, question in question_section.question.items():
            logger.info(f"{question} ({language}) ... ")
            try:
                response = text2sparql(
                    endpoint=url,
                    dataset=file_model.dataset.id,
                    question=question,
                    database=database,
                    timeout=timeout,
                )
                answer: dict[str, str] = response.model_dump()
                if question_section.id and file_model.dataset.prefix:
                    answer["qname"] = (
                        f"{file_model.dataset.prefix}:{question_section.id}-{language}"
                    )
                    answer["uri"] = f"{file_model.dataset.id}{question_section.id}-{language}"
                responses.append(answer)
            except (requests.ConnectionError, requests.HTTPError, requests.ReadTimeout) as error:
                logger.error(str(error))
            except ValidationError as error:
                logger.debug(str(error))
                logger.error("validation error")
    click.secho(json.dumps(responses, indent=2))
