"""query RDF endpoing"""

from SPARQLWrapper import SPARQLWrapper, JSON

def get_json(query: str, endpoint: str, timeout: int = 180):
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(timeout)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        return sparql.query().convert()
    except Exception as e:
        print(f"-----------------------------------\nError: {e}")
        return {'head': {'link': [], 'vars': []}, 'results': {'distinct': False, 'ordered': True, 'bindings': []}}