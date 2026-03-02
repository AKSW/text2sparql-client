"""tests"""

import time
from pathlib import Path

from click.testing import CliRunner, Result

from text2sparql_client.cli import cli

FIXTURE_DIR = Path(__file__).parent / "fixtures"
CLI_RUNNER = CliRunner()


class AnnotatedResult:
    """Extended click.testing.Result class"""

    lines: list[str]
    line_count: int
    result: Result
    stdout: str
    output: str
    exit_code: int
    t_start: float | None
    t_end: float | None
    t_duration: float | None
    exception: BaseException | None

    def __init__(self, result: Result):
        self.result = result
        # prepare list of lines
        self.lines = self.result.stdout.splitlines()
        # count the output lines
        self.line_count = len(self.lines)
        # copy some attributes
        self.stdout = result.stdout
        self.exit_code = result.exit_code
        self.output = result.output
        if result.exception:
            self.exception = result.exception


def _run(command: tuple[str, ...] | list[str]) -> AnnotatedResult:
    """Wrap the CliRunner"""
    t_start = time.time()
    result = CLI_RUNNER.invoke(cli, command)
    t_end = time.time()
    annotated_result = AnnotatedResult(result=result)
    annotated_result.t_start = t_start
    annotated_result.t_end = t_end
    annotated_result.t_duration = t_end - t_start
    return annotated_result


def run(command: tuple[str, ...] | list[str]) -> AnnotatedResult:
    """Wrap the CliRunner, asserting exit 0"""
    result = _run(command)
    command_string = " ".join([str(_) for _ in command])
    assert result.exit_code == 0, (
        f"On executing '{command_string}', "
        f"exit code should be 0 (but was {result.exit_code}). "
        f"Details: {result.result.exception}"
    )
    return result


def run_without_assertion(command: tuple[str, ...] | list[str]) -> AnnotatedResult:
    """Wrap the CliRunner but does not assert anything"""
    return _run(command=command)


def run_asserting_error(command: tuple[str, ...] | list[str], match: str) -> AnnotatedResult:
    """Wrap the CliRunner, asserting exit 1 or more"""
    result = _run(command=command)
    assert result.exit_code >= 1, f"exit code should be 1 or more (but was {result.exit_code})"
    assert match in result.stdout or match in str(result.result) or match in str(result.output)
    return result
