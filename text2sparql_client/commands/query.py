"""query endpoint command"""

import json
import sys
from io import TextIOWrapper
from pathlib import Path

import click
import yaml
from loguru import logger
from tqdm import tqdm

from text2sparql_client.utils.evaluation_metrics import DBpediaDict2PytrecDict
from text2sparql_client.utils.language_list import LanguageList
from text2sparql_client.utils.query_rdf import get_json


def check_output_file(file: str) -> None:
    """Check if output file already exists."""
    if Path(file).exists():
        logger.error(f"Output file {file} already exists.")
        sys.exit(1)


def generate_true_result_set(test_dataset: dict, endpoint: str, languages: list[type[str]]) -> dict:
    """Generate the gold truth result set from the QUESTIONS_FILE."""
    dataset_prefix = test_dataset["dataset"]["prefix"]

    ground_truth = {}

    order_required = []

    for question in tqdm(test_dataset["questions"]):
        for lang in languages:
            result_true = get_json(question["query"]["sparql"], endpoint)
            yml_qname = f"{dataset_prefix}:{question['id']}-{lang}"

            db2pytrec = DBpediaDict2PytrecDict(yml_qname)
            result_true = db2pytrec.tranform(result_true)

            ground_truth.update(result_true)

            if "features" in question:  # noqa: SIM102
                if "RESULT_ORDER_MATTERS" in question["features"]:
                    order_required.append(yml_qname)

    if order_required:
        ground_truth["order_required"] = order_required

    return ground_truth


def generate_pred_result_set(
    json_answers: dict, test_dataset: dict, endpoint: str, languages: list[type[str]]
) -> dict:
    """Generate the predicted result set from the ANSWERS_FILE."""
    dataset_prefix = test_dataset["dataset"]["prefix"]

    predicted = {}

    for question in tqdm(test_dataset["questions"]):
        for lang in languages:
            yml_qname = f"{dataset_prefix}:{question['id']}-{lang}"

            try:
                response_idx = next(
                    i for i, response in enumerate(json_answers) if response["qname"] == yml_qname
                )
                result_predicted = get_json(json_answers[response_idx]["query"], endpoint)
            except StopIteration:
                logger.info(f"\n-------\nqname {yml_qname} not found in responses\n-------\n")
                result_predicted = {
                    "head": {"link": [], "vars": []},
                    "results": {"distinct": False, "ordered": True, "bindings": []},
                }

            db2pytrec = DBpediaDict2PytrecDict(yml_qname)
            result_predicted = db2pytrec.tranform(result_predicted)

            predicted.update(result_predicted)

    return predicted


@click.command(name="query")
@click.argument("QUESTIONS_FILE", type=click.File())
@click.option(
    "--answers_file",
    "-a",
    type=click.File(),
    default=None,
    show_default=True,
    help="File containing automatically generated answers for the questions "
    "when generating predicted result set. If not provided, the true result "
    "set will be generated instead.",
)
@click.option(
    "--endpoint",
    "-e",
    type=click.STRING,
    default="http://141.57.8.18:9080/sparql",
    show_default=True,
    help="RDF endpoint URL for that dataset.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(allow_dash=True, dir_okay=False),
    default="-",
    show_default=True,
    help="Which file to save the result_set.",
)
@click.option(
    "--languages",
    "-l",
    type=LanguageList(),
    default="['en']",
    show_default=True,
    help="List of languages represented in the QUESTIONS_FILE.",
)
def query_command(
    questions_file: TextIOWrapper,
    answers_file: TextIOWrapper,
    endpoint: str,
    output: str,
    languages: list[type[str]],
) -> None:
    """Query the RDF endpoint with the queries in the QUESTIONS_FILE or ANSWERS_FILE.

    The result set will be saved to the file specified by OUTPUT.
    If ANSWERS_FILE is provided, it will be used to generate the predicted result set instead.
    """
    check_output_file(file=output)

    test_dataset = yaml.safe_load(questions_file)
    if answers_file:
        json_answers = json.load(answers_file)
        result_set = generate_pred_result_set(json_answers, test_dataset, endpoint, languages)
    else:
        result_set = generate_true_result_set(test_dataset, endpoint, languages)

    logger.info(f"Writing {len(result_set)} results to {output if output != '-' else 'stdout'}.")
    with click.open_file(filename=output, mode="w", encoding="UTF-8") as file:
        json.dump(result_set, file, indent=2)
