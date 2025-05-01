"""query command"""

import json
import sys
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


def check_output_file(file: str) -> None:
    """Check if output file already exists."""
    if Path(file).exists():
        logger.error(f"Output file {file} already exists.")
        sys.exit(1)


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
    default=600,
    show_default=True,
    help="Timeout in seconds.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, file_okay=True, allow_dash=True),
    default="-",
    show_default=True,
    help="Save JSON output to this file.",
)
@click.option(
    "--cache/--no-cache",
    default=True,
    show_default=True,
    help="If possible, return a cached response from the answers database.",
)
def ask_command(  # noqa: PLR0913
    questions_file: TextIOWrapper,
    url: str,
    answers_db: str,
    timeout: int,
    output: str,
    cache: bool,
) -> None:
    """Query a TEXT2SPARQL endpoint

    Use a questions YAML file and send each question to a TEXT2SPARQL conform endpoint.
    This command will create a sqlite database (--answers-db) saving the responses.
    """
    database = Database(file=Path(answers_db))
    file_model = QuestionsFile.model_validate(yaml.safe_load(questions_file))
    logger.info(f"Asking questions about dataset {file_model.dataset.id} on endpoint {url}.")
    check_output_file(file=output)
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
                    cache=cache,
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
    check_output_file(file=output)
    logger.info(f"Writing {len(responses)} responses to {output if output != '-' else 'stdout'}.")
    with click.open_file(filename=output, mode="w", encoding="UTF-8") as file:
        json.dump(responses, file, indent=2)
