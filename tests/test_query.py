"""Test queries"""

from tests import run, run_asserting_error
from tests.conftest import QuestionsFiles, ServerFixture, is_json_file


def test_noop() -> None:
    """Test noop starts"""
    assert "TEXT2SPARQL Client" in run(command=["--help"]).stdout
    assert run(command=["--version"]).line_count == 1


def test_successful_runs(server: ServerFixture, questions_files: QuestionsFiles) -> None:
    """Test successful requests."""
    run(command=("ask", str(questions_files.questions), server.get_url()))
    run(command=("ask", str(questions_files.with_ids), server.get_url()))


def test_non_successful_runs(server: ServerFixture, questions_files: QuestionsFiles) -> None:
    """Test non-successful requests."""
    run_asserting_error(
        command=("ask", str(questions_files.non_unique_ids), server.get_url()),
        match="Questions must have unique ids",
    )
    run_asserting_error(
        command=("ask", str(questions_files.partial_ids), server.get_url()),
        match="Only some questions have a ID",
    )


def test_output(server: ServerFixture, questions_files: QuestionsFiles) -> None:
    """Test different output files."""
    output = "output.json"
    run(command=("ask", str(questions_files.questions), server.get_url(), "-o", output))
    run_asserting_error(
        command=("ask", str(questions_files.questions), server.get_url(), "-o", output),
        match="already exists.",
    )
    assert is_json_file(output), "Output file should be JSON."
