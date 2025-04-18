"""database backend for the responses"""

import pickle
import sqlite3
from pathlib import Path

from requests import Response


class Database:
    """Database backend for the responses"""

    def __init__(self, file: Path):
        self.connection = sqlite3.connect(file.absolute())
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                time VARCHAR,
                endpoint VARCHAR,
                dataset VARCHAR,
                question VARCHAR,
                response VARCHAR,
                exception VARCHAR
            )
            """
        )
        cursor.close()

    def register_question(self, time: str, endpoint: str, dataset: str, question: str) -> None:
        """Register a new question"""
        with self.connection as cursor:
            cursor.execute(
                """
                INSERT INTO responses (time, endpoint, dataset, question)
                VALUES (?, ?, ?, ?)
                """,
                (
                    time,
                    endpoint,
                    dataset,
                    question,
                ),
            )

    def add_response(
        self, time: str, endpoint: str, dataset: str, question: str, response: Response
    ) -> None:
        """Add a response to the database"""
        with self.connection as cursor:
            cursor.execute(
                """
                UPDATE responses
                SET response=?
                WHERE time=? AND endpoint=? AND dataset=? AND question=?
                """,
                (
                    pickle.dumps(response),
                    time,
                    endpoint,
                    dataset,
                    question,
                ),
            )

    def add_exception(
        self, time: str, endpoint: str, dataset: str, question: str, exception: Exception
    ) -> None:
        """Add an exception to the database"""
        with self.connection as cursor:
            cursor.execute(
                """
                UPDATE responses
                SET exception=?
                WHERE time=? AND endpoint=? AND dataset=? AND question=?
                """,
                (
                    pickle.dumps(exception),
                    time,
                    endpoint,
                    dataset,
                    question,
                ),
            )
