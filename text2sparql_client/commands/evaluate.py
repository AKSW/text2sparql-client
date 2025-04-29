"""evaluate command"""

import json
import yaml
import sys
import re
import ast
import click

from io import TextIOWrapper
from pathlib import Path
from loguru import logger
from tqdm import tqdm

from text2sparql_client.utils.evaluation_metrics import Evaluation, DBpediaDict2PytrecDict
from text2sparql_client.utils.query_rdf import get_json

class LanguageList(click.ParamType):
    name = "languageList"

    def convert(self, value: str, param: click.Parameter | None, ctx: click.Context | None) -> list:
        def is_valid_language_list(s):
            return re.match(pattern, s) is not None
        pattern = r"^\[\s*'(?:[a-z]{2})'\s*(,\s*'(?:[a-z]{2})'\s*)*\]$"
        languages = None
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
    help="RDF endpoint URL for that dataset."
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, allow_dash=True),
    default="-",
    show_default=True,
    help="Which file to save the results."
)
@click.option(
    "--languages",
    "-l",
    type=LanguageList(),
    default="['en']",
    show_default=True,
    help="List of languages where the questions are represented in the QUESTIONS_FILE."
)
def evaluate_command(
    api_name: str,
    questions_file: TextIOWrapper,
    response_file: TextIOWrapper,
    endpoint: str,
    output: str,
    languages: list,
) -> None:
    """Evaluate the resuls from a TEXT2SPARQL endpoint
    
    Use a questions YAML and a response JSON with answers collected from a TEXT2SPARQL conform api.
    This command will create a JSON file with the metric values using the pytrec_eval library."""

    test_dataset = yaml.safe_load(questions_file)
    response_file = json.load(response_file)

    dataset_prefix = test_dataset['dataset']['prefix']

    ground_truth = {}
    predicted = {}

    for question in tqdm(test_dataset['questions']):
        for lang in languages:
            result_true = get_json(question['query']['sparql'], question['question'][lang], endpoint=endpoint)
            yml_qname = f"{dataset_prefix}:{question['id']}-{lang}"
            try:
                response_idx = [i for i, response in enumerate(response_file) if response['qname'] == yml_qname][0]
            except IndexError as e:
                print(f"\n-------\nqname {yml_qname} not found in responses\n-------\n")
                raise e
            
            result_predicted = get_json(response_file[response_idx]['query'], question['question'][lang], endpoint=endpoint)

            db2pytrec = DBpediaDict2PytrecDict(f"{dataset_prefix}:{question['id']}-{lang}")
            result_predicted = db2pytrec.tranform(result_predicted)
            result_true = db2pytrec.tranform(result_true)

            ground_truth.update(result_true)
            predicted.update(result_predicted) 
    
    evaluation = Evaluation(api_name)
    results = evaluation.evaluate(predicted, ground_truth)

    print(f"Results:\n{results}")

    check_output_file(file=output)
    logger.info(f"Writing {len(results)} responses to {output if output != '-' else 'stdout'}.")
    with click.open_file(filename=output, mode="w", encoding="UTF-8") as file:
        json.dump(results, file, indent=2)