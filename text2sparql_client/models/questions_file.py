"""questions file"""

from typing import Self

from loguru import logger
from pydantic import BaseModel, model_validator


class Question(BaseModel):
    """Question (pydantic model)"""

    id: int | None = None
    question: dict[str, str]


class DatasetDescription(BaseModel):
    """Dataset (pydantic model)"""

    id: str
    prefix: str | None = None


class QuestionsFile(BaseModel):
    """Questions File (pydantic model)"""

    dataset: DatasetDescription
    questions: list[Question]

    @model_validator(mode="after")
    def validate_question_ids(self) -> Self:
        """Validate for unique question IDs"""
        ids = [_.id for _ in self.questions]
        unique_ids = set(ids)
        if len(unique_ids) == 1 and next(iter(unique_ids)) is None:
            logger.info("No question IDs found")
            return self
        if None in ids:
            raise ValueError("Only some questions have a ID")
        if len(unique_ids) != len(ids):
            raise ValueError("Questions must have unique ids")
        return self
