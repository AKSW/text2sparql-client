"""test questions file"""

import pytest
import yaml

from tests.conftest import QuestionsFiles
from text2sparql_client.models.questions_file import QuestionsFile


def test_validation(questions_files: QuestionsFiles) -> None:
    """Test success validation of questions file."""
    for valid_file in (
        questions_files.questions,
        questions_files.with_ids,
        questions_files.bad,
    ):
        with valid_file.open() as f:
            QuestionsFile.model_validate(yaml.safe_load(f))


def test_validation_unique_ids(questions_files: QuestionsFiles) -> None:
    """Test unique id validation of questions file."""
    with (
        pytest.raises(ValueError, match="Questions must have unique ids"),
        questions_files.non_unique_ids.open() as f,
    ):
        QuestionsFile.model_validate(yaml.safe_load(f))


def test_validation_all_or_no_ids(questions_files: QuestionsFiles) -> None:
    """Test all or no id validation of questions file."""
    with (
        pytest.raises(ValueError, match="Only some questions have a ID"),
        questions_files.partial_ids.open() as f,
    ):
        QuestionsFile.model_validate(yaml.safe_load(f))
