"""pytest config"""

from collections.abc import Generator
from http import HTTPStatus
from multiprocessing import Process
from os import chdir
from pathlib import Path
from time import sleep
from typing import Any

import pytest
from requests import exceptions, get

from tests import FIXTURE_DIR
from text2sparql_client.commands.serve import run_service


class ServerFixture:
    """Server fixture"""

    max_tries: int = 10
    host: str
    port: int
    process: Process

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def get_url(self) -> str:
        """Get URL of the Service"""
        return f"http://{self.host}:{self.port}"

    def kill(self) -> None:
        """Kill the Service"""
        self.process.kill()

    def start(self) -> None:
        """Start the Service"""
        self.process = Process(target=run_service, args=(self.host, self.port), daemon=True)
        self.process.start()
        is_up = False
        test_tries = 0
        while not is_up and test_tries < self.max_tries:
            try:
                sleep(0.5)
                response = get(self.get_url(), timeout=5)
                if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                    is_up = True
            except exceptions.ConnectionError:
                test_tries += 1


@pytest.fixture(scope="module")
def server() -> Generator[ServerFixture, Any, None]:
    """Provide server fixture"""
    server = ServerFixture(host="127.0.0.1", port=8000)
    server.start()
    yield server
    server.kill()


class QuestionsFiles:
    """Fixture data for test"""

    questions = FIXTURE_DIR / "questions.yml"
    bad = FIXTURE_DIR / "bad.yml"
    partial_ids = FIXTURE_DIR / "partial_ids.yml"
    with_ids = FIXTURE_DIR / "with-ids.yml"
    non_unique_ids = FIXTURE_DIR / "non-unique_ids.yml"


@pytest.fixture
def questions_files() -> QuestionsFiles:
    """Provide FixtureData"""
    return QuestionsFiles()


@pytest.fixture(autouse=True)
def new_dir(tmp_path: Path) -> Generator[Path, Any, None]:
    """Provide new test directory"""
    current_directory = Path.cwd()
    chdir(tmp_path)
    yield tmp_path
    # switch back to original directory
    chdir(current_directory)
