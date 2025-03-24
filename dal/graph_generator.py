import os

from neo4j import GraphDatabase
from typing import List

from models.types import RelationalDataEntry


class Neo4jService:
    def __init__(self):
        AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", ""))
        
        self.driver = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://localhost:7687"), auth=AUTH)
        with self.driver.session() as session:
            result = session.run("RETURN 1 as n")
            print(f"Connection successful: {result.single()['n']}")
    
    def close(self):
        self.driver.close()
    
    def create_graph(self, data: List[RelationalDataEntry]):
        with self.driver.session() as session:
            for entry in data:
                self._process_entry(session, entry)
            self._verify_graph(session)
    
    def _process_entry(self, session, entry: RelationalDataEntry):
        query = """
        MERGE (character:Character {name: $character})
        MERGE (team:Team {name: $team})
        MERGE (character)-[:MEMBER_OF]->(team)

        MERGE (gene:Gene {name: $gene})
        MERGE (character)-[:HAS_MUTATION]->(gene)

        MERGE (power:Power {name: $power})
        MERGE (character)-[:POSSESSES_POWER]->(power)

        MERGE (gene)-[:CONFERS]->(power)

        RETURN character.name AS Character, team.name AS Team, gene.name AS Gene, power.name AS Power
        """
        
        result = session.run(
            query,
            character=entry.character,
            team=entry.team,
            gene=entry.gene,
            power=entry.power
        )
        
        print(f"Processed")
        for record in result:
            print(f"Character: {record['Character']}. Team: {record['Team']}")
            print("---")
    
    def _verify_graph(self, session):
        print("\nRunning verification queries:")
        
        # Test query 1: Find all teams and their members
        team_result = session.run("""
            MATCH (character:Character)-[:MEMBER_OF]->(team:Team)
            RETURN team.name AS Team, collect(character.name) AS Members
        """)
        
        print("Teams and Members:")
        for record in team_result:
            print(f"{record['Team']}: {', '.join(record['Members'])}")
        
        # Test query 2: Find powers by gene
        gene_result = session.run("""
            MATCH (gene:Gene)-[:CONFERS]->(power:Power)
            RETURN gene.name AS Gene, power.name AS Power
        """)
        
        print("\nGenes and their Powers:")
        for record in gene_result:
            print(f"{record['Gene']}: {record['Power']}")

#  TODO multiple genes and powers!
#  TODO fix waringin onaggregation skips null values
    def query_character(self, name: str, include_mutual: bool = False):
        base_query = """
        MATCH (char:Character {name: $name})
        OPTIONAL MATCH (char)-[:POSSESSES_POWER]->(power:Power)
        OPTIONAL MATCH (char)-[:HAS_MUTATION]->(gene:Gene)
        OPTIONAL MATCH (char)-[:MEMBER_OF]->(team:Team)
        """

        if include_mutual:
            query = base_query + """
            WITH char, collect(power.name) as powers, collect(gene.name) as genes, team
            OPTIONAL MATCH (char)-[relationship]-(shared)
            WHERE shared IS NOT NULL
            WITH char, powers, genes, team, shared
            OPTIONAL MATCH (other:Character)-[relationship2]->(shared)
            WHERE other.name <> char.name
            WITH char, powers, genes, team, shared.name as sharedNode,
                 collect(DISTINCT other.name) as others
            WHERE size(others) > 0
            RETURN char.name as Character,
                   powers as Powers,
                   genes as Genes,
                   team.name as Team,
                   collect({
                       shared: sharedNode,
                       others: others
                   }) as mutualConnections
            """
        else:
            query = base_query + """
            RETURN char.name as Character,
                   collect(power.name) as Powers,
                   collect(gene.name) as Genes,
                   team.name as Team
            """
            query = base_query + """
            RETURN char.name as Character,
                   collect(power.name) as Powers,
                   collect(gene.name) as Genes,
                   team.name as Team
            """
        
        result = self.driver.session().run(query, name=name)
        return result.single()
#  TODO query each type of node?
