"""Test evaluate"""

from tests import run, run_asserting_error
from tests.conftest import QuestionsFiles, ResponsesFiles


def test_successful_evaluation(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test successful evaluation."""
    run(
        command=(
            "evaluate",
            "api_name",
            str(questions_files.with_ids),
            str(responses_files.responses),
        )
    )


def test_non_successful_evaluation(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test non-successful evaluation."""
    run_asserting_error(
        command=("evaluate", "api_name", str(questions_files.non_unique_ids)),
        match="Missing argument",
    )
    run_asserting_error(
        command=("evaluate", str(questions_files.partial_ids), str(responses_files.responses)),
        match="Missing argument",
    )


def test_output_evaluation(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test evaluation with output file."""
    output = "evaluation.json"
    run(
        command=(
            "evaluate",
            "api_name",
            str(questions_files.questions),
            str(responses_files.responses),
            "-o",
            output,
        )
    )
    run_asserting_error(
        command=(
            "evaluate",
            "api_name",
            str(questions_files.questions),
            str(responses_files.responses),
            "-o",
            output,
        ),
        match="already exists.",
    )
