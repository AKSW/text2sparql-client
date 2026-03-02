"""Test queries"""

from tests import run, run_asserting_error, run_without_assertion
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


def test_timeout_handling_and_loggin(
    server: ServerFixture, questions_files: QuestionsFiles
) -> None:
    """Test timeout handling and logging requests."""
    command = (
        "ask",
        "--timeout",
        "1",
        "--retries",
        "2",
        "--retry-sleep",
        "0",
        "--retries-log",
        "-",
        "-o",
        "output.json",
        str(questions_files.with_ids),
        server.get_url(),
    )
    result = run_without_assertion(command=command)
    assert "Read timed out" in result.output
    assert "Retrying" in result.output
    assert "Maximum number of retries reached" in result.output


def test_output(server: ServerFixture, questions_files: QuestionsFiles) -> None:
    """Test different output files."""
    output = "output.json"
    run(command=("ask", "-o", output, str(questions_files.with_ids), server.get_url()))
    run_asserting_error(
        command=("ask", "-o", output, str(questions_files.with_ids), server.get_url()),
        match="already exists.",
    )
    assert is_json_file(output), "Output file should be JSON."


def test_cached_response(server: ServerFixture, questions_files: QuestionsFiles) -> None:
    """Test cached response."""
    command = ("ask", str(questions_files.with_ids), server.get_url())
    assert "Cached response found." not in run(command=command).output
    assert "Cached response found." in run(command=command).output
    assert "Cached response found." not in run(command=(*command, "--no-cache")).output
