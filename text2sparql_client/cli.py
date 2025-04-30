"""cli"""

from importlib.metadata import version
from sys import version_info

import click

from text2sparql_client.commands.ask import ask_command
from text2sparql_client.commands.evaluate import evaluate_command
from text2sparql_client.commands.serve import serve_command
from text2sparql_client.context import ApplicationContext


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=version("text2sparql-client"),
    message="%(prog)s %(version)s "
    f"(Python {version_info.major}.{version_info.minor}.{version_info.micro})",
)
@click.option("--debug", "-d", is_flag=True, help="Enable output of debug information.")
@click.pass_context
def cli(ctx: click.core.Context, debug: bool) -> None:
    """TEXT2SPARQL Client

    This command line tool can be used to retrieve answers from a TEXT2SPARQL conform server.

    For information on the TEXT2SPARQL challenge, have a look at: https://text2sparql.aksw.org/
    """
    ctx.obj = ApplicationContext(debug=debug)


cli.add_command(ask_command)
cli.add_command(serve_command)
cli.add_command(evaluate_command)
