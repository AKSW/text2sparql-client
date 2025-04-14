"""Test queries"""

from tests import run


def test_noop_start() -> None:
    """Test noop starts"""
    assert "TEXT2SPARQL Client" in run(command=["--help"]).stdout
    assert run(command=["--version"]).line_count == 1
