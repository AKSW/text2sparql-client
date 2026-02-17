"""Test evaluate"""

import pytest

from tests import run, run_asserting_error, run_without_assertion
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
    result = run_without_assertion(
        command=(
            "evaluate",
            "-l",
            "en, de",
            "api_name",
            str(result_sets_files.result_set),
            str(result_sets_files.result_set),
        )
    )
    assert result.exit_code >= 1, f"exit code should be 1 or more (but was {result.exit_code})"


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


@pytest.mark.skip(reason="tests that require output to be save are currently disabled")
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
