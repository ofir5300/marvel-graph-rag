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
    def query_character(self, name: str):
        query = """
        MATCH (char:Character {name: $name})
        OPTIONAL MATCH (char)-[:POSSESSES_POWER]->(power:Power)
        OPTIONAL MATCH (char)-[:HAS_MUTATION]->(gene:Gene)
        OPTIONAL MATCH (char)-[:MEMBER_OF]->(team:Team)
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
               collect({shared: sharedNode, others: others}) as Connections
        """
        result = self.driver.session().run(query, name=name)
        return result.single()
    
    def query_power(self, name: str):
        query = """
        MATCH (power:Power {name: $name})
        OPTIONAL MATCH (char:Character)-[:POSSESSES_POWER]->(power)
        OPTIONAL MATCH (gene:Gene)-[:ENABLES]->(power)
        WITH power, collect(char.name) as characters, collect(gene.name) as genes
        RETURN power.name as Power,
               characters as Characters,
               genes as Genes
        """
        result = self.driver.session().run(query, name=name)
        return result.single()
    
    def query_gene(self, name: str):
        query = """
        MATCH (gene:Gene {name: $name})
        OPTIONAL MATCH (char:Character)-[:HAS_MUTATION]->(gene)
        OPTIONAL MATCH (gene)-[:ENABLES]->(power:Power)
        WITH gene, collect(char.name) as characters, collect(power.name) as powers
        RETURN gene.name as Gene,
               characters as Characters,
               powers as Powers
        """
        result = self.driver.session().run(query, name=name)
        return result.single()
    
    def query_team(self, name: str):
        query = """
        MATCH (team:Team {name: $name})
        OPTIONAL MATCH (char:Character)-[:MEMBER_OF]->(team)
        WITH team, collect(char.name) as members
        OPTIONAL MATCH (char:Character)-[:MEMBER_OF]->(team)
        OPTIONAL MATCH (char)-[:POSSESSES_POWER]->(power:Power)
        OPTIONAL MATCH (char)-[:HAS_MUTATION]->(gene:Gene)
        RETURN team.name as Team,
               members as Members,
               collect(DISTINCT power.name) as TeamPowers,
               collect(DISTINCT gene.name) as TeamGenes
        """
        result = self.driver.session().run(query, name=name)
        return result.single()
