"""evaluate command"""

import ast
import json
import re
import sys
from io import TextIOWrapper
from pathlib import Path

import click
import yaml
from loguru import logger
from tqdm import tqdm

from text2sparql_client.utils.evaluation_metrics import DBpediaDict2PytrecDict, Evaluation
from text2sparql_client.utils.order_matters import (
    combine_metrics,
    filter_answer_dict,
    non_destructive_update,
)
from text2sparql_client.utils.query_rdf import get_json


class LanguageList(click.ParamType):
    """Custom Click parameter type for validating language list input."""

    name = "languageList"

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[type[str]]:
        """Convert and validate a string input into a list of language codes."""

        def is_valid_language_list(s: str) -> bool:
            return re.match(pattern, s) is not None

        pattern = r"^\[\s*'(?:[a-z]{2})'\s*(,\s*'(?:[a-z]{2})'\s*)*\]$"
        languages: list[type[str]] = []
        if is_valid_language_list(value):
            languages = ast.literal_eval(value)
        else:
            self.fail(f"{value!r} is not a valid language list", param, ctx)
        return languages


def check_output_file(file: str) -> None:
    """Check if output file already exists."""
    if Path(file).exists():
        logger.error(f"Output file {file} already exists.")
        sys.exit(1)


@click.command(name="evaluate")
@click.argument("API_NAME", type=click.STRING)
@click.argument("QUESTIONS_FILE", type=click.File())
@click.argument("RESPONSES_FILE", type=click.File())
@click.option(
    "--endpoint",
    "-e",
    type=click.STRING,
    default="http://141.57.8.18:8895/sparql",
    show_default=True,
    help="RDF endpoint URL for that dataset.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(allow_dash=True, dir_okay=False),
    default="-",
    show_default=True,
    help="Which file to save the results.",
)
@click.option(
    "--languages",
    "-l",
    type=LanguageList(),
    default="['en']",
    show_default=True,
    help="List of languages where the questions are represented in the QUESTIONS_FILE.",
)
@click.option(
    "--order_metric",
    "-m",
    type=click.STRING,
    default="ndcg",
    show_default=True,
    help="Performance metric to be used for questions flagged with RESULT_ORDER_MATTERS.",
)
def evaluate_command(  # noqa: PLR0913
    api_name: str,
    questions_file: TextIOWrapper,
    responses_file: TextIOWrapper,
    endpoint: str,
    output: str,
    languages: list,
    order_metric: str,
) -> None:
    """Evaluate the resuls from a TEXT2SPARQL endpoint.

    Use a questions YAML and a response JSON with answers collected from a TEXT2SPARQL conform api.
    This command will create a JSON file with the metric values using the pytrec_eval library.
    """
    test_dataset = yaml.safe_load(questions_file)
    json_file = json.load(responses_file)

    dataset_prefix = test_dataset["dataset"]["prefix"]

    ground_truth = {}
    predicted = {}

    order_required = []

    for question in tqdm(test_dataset["questions"]):
        for lang in languages:
            result_true = get_json(question["query"]["sparql"], endpoint)
            yml_qname = f"{dataset_prefix}:{question['id']}-{lang}"

            try:
                response_idx = next(
                    i for i, response in enumerate(json_file) if response["qname"] == yml_qname
                )
                result_predicted = get_json(json_file[response_idx]["query"], endpoint)
            except StopIteration:
                logger.info(f"\n-------\nqname {yml_qname} not found in responses\n-------\n")
                result_predicted = {
                    "head": {"link": [], "vars": []},
                    "results": {"distinct": False, "ordered": True, "bindings": []},
                }

            db2pytrec = DBpediaDict2PytrecDict(f"{dataset_prefix}:{question['id']}-{lang}")
            result_predicted = db2pytrec.tranform(result_predicted)
            result_true = db2pytrec.tranform(result_true)

            ground_truth.update(result_true)
            predicted.update(result_predicted)

            if "features" in question:  # noqa: SIM102
                if "RESULT_ORDER_MATTERS" in question["features"]:
                    order_required.append(f"{dataset_prefix}:{question['id']}-{lang}")

    evaluation = Evaluation(api_name)
    results = evaluation.evaluate(predicted, ground_truth)

    if order_required:
        filtered_ground_truth = filter_answer_dict(ground_truth, order_required)
        filtered_predicted = filter_answer_dict(predicted, order_required)
        filtered_results = Evaluation(api_name, metrics={order_metric}).evaluate(
            filtered_predicted, filtered_ground_truth
        )

        non_destructive_update(results, filtered_results, order_metric)

        combine_metrics(results, order_metric)

    check_output_file(file=output)
    logger.info(f"Writing {len(results)} results to {output if output != '-' else 'stdout'}.")
    with click.open_file(filename=output, mode="w", encoding="UTF-8") as file:
        json.dump(results, file, indent=2)
