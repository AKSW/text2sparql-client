"""test questions file"""

import pytest
import yaml

from tests import FIXTURE_DIR
from text2sparql_client.models.questions_file import QuestionsFile


class FixtureData:
    """Fixture data for test"""

    questions = FIXTURE_DIR / "questions.yml"
    bad = FIXTURE_DIR / "bad.yml"
    partial_ids = FIXTURE_DIR / "partial_ids.yml"
    with_ids = FIXTURE_DIR / "with-ids.yml"
    non_unique_ids = FIXTURE_DIR / "non-unique_ids.yml"


@pytest.fixture
def fixture_data() -> FixtureData:
    """Provide FixtureData"""
    return FixtureData()


def test_validation(fixture_data: FixtureData) -> None:
    """Test success validation of questions file."""
    for valid_file in (
        fixture_data.questions,
        fixture_data.with_ids,
        fixture_data.bad,
    ):
        with valid_file.open() as f:
            QuestionsFile.model_validate(yaml.safe_load(f))


def test_validation_unique_ids(fixture_data: FixtureData) -> None:
    """Test unique id validation of questions file."""
    with (
        pytest.raises(ValueError, match="Questions must have unique ids"),
        fixture_data.non_unique_ids.open() as f,
    ):
        QuestionsFile.model_validate(yaml.safe_load(f))


def test_validation_all_or_no_ids(fixture_data: FixtureData) -> None:
    """Test all or no id validation of questions file."""
    with (
        pytest.raises(ValueError, match="Only some questions have a ID"),
        fixture_data.partial_ids.open() as f,
    ):
        QuestionsFile.model_validate(yaml.safe_load(f))
