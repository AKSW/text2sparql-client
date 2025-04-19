"""test serve"""

from http import HTTPStatus

from requests import get

from tests.conftest import ServerFixture
from text2sparql_client.commands.serve import KNOWN_DATASETS


def test_unprocessable(server: ServerFixture) -> None:
    """Test unprocessable requests."""
    unprocessable = get(server.get_url(), timeout=5)
    assert unprocessable.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    not_found = get(server.get_url(), params={"dataset": KNOWN_DATASETS[0]}, timeout=5)
    assert not_found.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    not_found = get(server.get_url(), params={"question": "only question - no dataset"}, timeout=5)
    assert not_found.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_data(server: ServerFixture) -> None:
    """Test wrong-data requests."""
    not_found = get(
        server.get_url(), params={"dataset": "no-valid-dataset", "question": "..."}, timeout=5
    )
    assert not_found.status_code == HTTPStatus.NOT_FOUND


def test_success(server: ServerFixture) -> None:
    """Test successful requests."""
    found = get(
        server.get_url(), params={"dataset": KNOWN_DATASETS[0], "question": "..."}, timeout=5
    )
    assert found.status_code == HTTPStatus.OK
