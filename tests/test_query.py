"""Test query"""

from tests import run, run_asserting_error
from tests.conftest import QuestionsFiles, ResponsesFiles, is_json_file


def test_successful_true_query(questions_files: QuestionsFiles) -> None:
    """Test successful query."""
    run(
        command=(
            "query",
            str(questions_files.with_ids),
        )
    )


def test_successful_pred_query(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test successful query."""
    run(
        command=(
            "query",
            "-a",
            str(responses_files.responses),
            str(questions_files.with_ids),
        )
    )


def test_non_successful_query(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test non-successful query."""
    run_asserting_error(
        command=("query", str(questions_files.non_unique_ids)),
        match="KeyError",
    )
    run_asserting_error(
        command=("query", "-a", str(responses_files.responses), str(questions_files.partial_ids)),
        match="KeyError",
    )


def test_language_query_error(
    questions_files: QuestionsFiles, responses_files: ResponsesFiles
) -> None:
    """Test query with language option error."""
    run_asserting_error(
        command=(
            "query",
            "-a",
            str(responses_files.responses),
            "-l",
            "en, de",
            str(questions_files.with_ids),
        ),
        match="not a valid language list",
    )


def test_output_query(questions_files: QuestionsFiles, responses_files: ResponsesFiles) -> None:
    """Test query with output file."""
    output = "output.json"
    run(
        command=(
            "query",
            "-a",
            str(responses_files.responses),
            "-o",
            output,
            str(questions_files.with_ids),
        )
    )
    run_asserting_error(
        command=(
            "query",
            "-a",
            str(responses_files.responses),
            "-o",
            output,
            str(questions_files.with_ids),
        ),
        match="already exists.",
    )
    assert is_json_file(output), "Output file should be JSON."
