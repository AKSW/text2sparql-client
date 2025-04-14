"""Context object for the CLI"""

from datetime import UTC, datetime

import click


class ApplicationContext:
    """Context object for the CLI"""

    def __init__(self, debug: bool):
        self.debug = debug

    def echo_debug(self, message: str) -> None:
        """Output a debug message if --debug is enabled."""
        if self.debug:
            now = datetime.now(tz=UTC)
            click.secho(f"[{now!s}] {message}", err=True, dim=True)

    @staticmethod
    def echo_info(message: str, nl: bool = True, fg: str = "") -> None:
        """Output an info message"""
        click.secho(message, nl=nl, fg=fg, err=True)
