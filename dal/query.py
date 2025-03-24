from dal.neo4j import Neo4jService

def query_character(name: str):
    service = Neo4jService()
    return service.query_character(name.lower())

def query_team(name: str):
    service = Neo4jService()
    return service.query_team(name.lower())

def query_gene(name: str):
    service = Neo4jService()
    return service.query_gene(name.lower())

def query_power(name: str):
    service = Neo4jService()
    return service.query_power(name.lower())