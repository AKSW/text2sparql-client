"""query RDF endpoing"""

import typing

from loguru import logger
from SPARQLWrapper import JSON, SPARQLWrapper


def get_json(query: str, endpoint: str, timeout: int = 180) -> dict | typing.Any:  # noqa: ANN401
    """Execute a SPARQL query and return the results as JSON.

    Args:
        query (str): The SPARQL query to execute
        endpoint (str): The SPARQL endpoint URL
        timeout (int): Query timeout in seconds

    Returns:
        dict: Query results in JSON format

    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(timeout)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        return sparql.query().convert()
    except Exception as e:  # noqa: BLE001
        logger.info(f"-----------------------------------\nError: {e}")
        return {
            "head": {"link": [], "vars": []},
            "results": {"distinct": False, "ordered": True, "bindings": []},
        }
