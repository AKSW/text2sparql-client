"""Custom Click parameter type for language list validation."""

import ast
import re

import click


class LanguageList(click.ParamType):
    """Custom Click parameter type for validating language list input."""

    name = "languageList"

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[type[str]]:
        """Convert and validate a string input into a list of language codes."""

        def is_valid_language_list(s: str) -> bool:
            return re.match(pattern, s) is not None

        pattern = r"^\[\s*'(?:[a-z]{2})'\s*(,\s*'(?:[a-z]{2})'\s*)*\]$"
        languages: list[type[str]] = []
        if is_valid_language_list(value):
            languages = ast.literal_eval(value)
        else:
            self.fail(f"{value!r} is not a valid language list", param, ctx)
        return languages
