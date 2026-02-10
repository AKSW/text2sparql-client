"""evaluate command"""

import json
import statistics
import sys
from io import TextIOWrapper
from pathlib import Path

import click
from loguru import logger

from text2sparql_client.utils.evaluation_metrics import (
    Evaluation,
    combine_averages,
    filter_answer_dict,
    non_destructive_update,
)
from text2sparql_client.utils.language_list import LanguageList


def order_matters(
    api_name: str, true_set: dict, pred_set: dict, results: dict, order_metric: str
) -> None:
    """Check if order matters for any of the questions and calculate the order_metric if necessary.

    Also generates the combined metric defined for text2sparql.
    """
    order_eval = Evaluation(api_name, metrics={order_metric})
    order_required = true_set["order_required"]
    filtered_predicted = filter_answer_dict(pred_set, order_required)
    filtered_true = filter_answer_dict(true_set, order_required)
    filtered_results = order_eval.evaluate(filtered_predicted, filtered_true)

    non_destructive_update(results, filtered_results, order_metric)
    combine_averages(results, order_metric)


def generate_language_averages(results: dict, languages: list[str], metrics: list[str]) -> None:
    """Generate average metrics across all questions for each metric and language."""
    language_averages = {language: {metric: [] for metric in metrics} for language in languages}
    for key, value in results.items():
        for metric in metrics:
            if metric in value:
                for language in languages:
                    if language in key:
                        language_averages[language][metric].append(value[metric])
    for language in languages:
        results[f"average-{language}"] = {
            metric: statistics.fmean(scores)
            for metric, scores in language_averages[language].items()
        }


def check_output_file(file: str) -> None:
    """Check if output file already exists."""
    if Path(file).exists():
        logger.error(f"Output file {file} already exists.")
        sys.exit(1)


@click.command(name="evaluate")
@click.argument("API_NAME", type=click.STRING)
@click.argument("TRUE_SET", type=click.File())
@click.argument("PRED_SET", type=click.File())
@click.option(
    "--output",
    "-o",
    type=click.Path(allow_dash=True, dir_okay=False),
    default="-",
    show_default=True,
    help="Which file to save the results.",
)
@click.option(
    "--order_metric",
    "-m",
    type=click.STRING,
    default="ndcg",
    show_default=True,
    help="Performance metric to be used for questions flagged with RESULT_ORDER_MATTERS.",
)
@click.option(
    "--languages",
    "-l",
    type=LanguageList(),
    default="['en']",
    show_default=True,
    help="List of languages to generate metrics results separately.",
)
def evaluate_command(  # noqa: PLR0913
    api_name: str,
    true_set: TextIOWrapper,
    pred_set: TextIOWrapper,
    output: str,
    order_metric: str,
    languages: list[type[str]],
) -> None:
    """Evaluate the resuls from a TEXT2SPARQL endpoint.

    Use a questions YAML and a response JSON with answers collected from a TEXT2SPARQL conform api.
    This command will create a JSON file with the metric values using the pytrec_eval library.
    """
    true_set = json.load(true_set)
    pred_set = json.load(pred_set)

    evaluator = Evaluation(api_name)
    results = evaluator.evaluate(pred_set, true_set)

    if "order_required" in true_set:
        order_matters(api_name, true_set, pred_set, results, order_metric)

    if len(languages) > 1:
        all_metrics = list(evaluator.metrics)
        if order_metric not in all_metrics:
            all_metrics.append(order_metric)
        generate_language_averages(results, languages, all_metrics)
        for language in languages:
            combine_averages(results, order_metric, average_field=f"average-{language}")

    check_output_file(file=output)
    logger.info(f"Writing {len(results)} results to {output if output != '-' else 'stdout'}.")
    with click.open_file(filename=output, mode="w", encoding="UTF-8") as file:
        json.dump(results, file, indent=2)
