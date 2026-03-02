"""Test evaluate"""

from tests import run, run_asserting_error
from tests.conftest import ResultSetsFiles, is_json_file


def test_successful_evaluation(result_sets_files: ResultSetsFiles) -> None:
    """Test successful evaluation."""
    run(
        command=(
            "evaluate",
            "api_name",
            str(result_sets_files.result_set),
            str(result_sets_files.result_set),
        )
    )


def test_language_evaluation_error(result_sets_files: ResultSetsFiles) -> None:
    """Test language option error in evaluation."""
    run_asserting_error(
        command=(
            "evaluate",
            "-l",
            "en, de",
            "api_name",
            str(result_sets_files.result_set),
            str(result_sets_files.result_set),
        ),
        match="not a valid language list",
    )


def test_missing_question_true_result_set(result_sets_files: ResultSetsFiles) -> None:
    """Test missing question in true result-set."""
    run_asserting_error(
        command=(
            "evaluate",
            "api_name",
            str(result_sets_files.result_set_missing),
            str(result_sets_files.result_set),
        ),
        match="KeyError",
    )


def test_output_evaluation(result_sets_files: ResultSetsFiles) -> None:
    """Test evaluation with output file."""
    output = "output.json"
    run(
        command=(
            "evaluate",
            "-o",
            output,
            "api_name",
            str(result_sets_files.result_set),
            str(result_sets_files.result_set),
        )
    )
    run_asserting_error(
        command=(
            "evaluate",
            "-o",
            output,
            "api_name",
            str(result_sets_files.result_set),
            str(result_sets_files.result_set),
        ),
        match="already exists.",
    )
    assert is_json_file(output), "Output file should be JSON."
