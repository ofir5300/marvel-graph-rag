from dal.graph_generator import Neo4jService

def query_character(name: str):
    service = Neo4jService()
    return service.query_character(name.lower(), include_mutual=True)

