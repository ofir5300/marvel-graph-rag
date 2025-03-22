import os, json, re
from neo4j import GraphDatabase
from typing import List, Dict, Any

class DataEntry:
    def __init__(self, character, team, genes, powers):
        self.character = character
        self.team = team
        self.genes = genes
        self.powers = powers

class Neo4jService:
    def __init__(self):
        AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", ""))
        
        self.driver = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://localhost:7687"), auth=AUTH)
        with self.driver.session() as session:
            result = session.run("RETURN 1 as n")
            print(f"Connection successful: {result.single()['n']}")
    
    def close(self):
        self.driver.close()
    
    def create_graph(self, data):


        with self.driver.session() as session:
            for entry in data:
                self._process_entry(session, entry)
            
            self._verify_graph(session)
    
    def _process_entry(self, session, entry):
        query = """
        // Merge Character node
        MERGE (character:Character {name: $character.name})
        SET character.realName = $character.realName
        
        // Merge Team node
        MERGE (team:Team {name: $team.name})
        
        // Create Character-Team relationship
        MERGE (character)-[:MEMBER_OF]->(team)
        
        // Process Genes
        WITH character, team
        UNWIND $genes AS geneData
        MERGE (gene:Gene {name: geneData.name})
        MERGE (character)-[:HAS_GENE]->(gene)
        
        // Process Powers
        WITH character, team
        UNWIND $powers AS powerData
        MERGE (power:Power {name: powerData.name})
        MERGE (character)-[:HAS_POWER]->(power)
        
        // Link Genes to Powers (simplified - in reality this might be more complex)
        WITH character, team
        MATCH (character)-[:HAS_GENE]->(gene)
        MATCH (character)-[:HAS_POWER]->(power)
        MERGE (gene)-[:ENABLES]->(power)
        
        RETURN character.name AS Character, team.name AS Team, 
               collect(DISTINCT gene.name) AS Genes, 
               collect(DISTINCT power.name) AS Powers
        """
        
        result = session.run(
            query,
            character=entry.character,
            team=entry.team,
            genes=entry.genes,
            powers=entry.powers
        )
        
        print(f"Processed {entry.character['name']}:")
        for record in result:
            print(f"Character: {record['Character']}")
            print(f"Team: {record['Team']}")
            print(f"Genes: {', '.join(record['Genes'])}")
            print(f"Powers: {', '.join(record['Powers'])}")
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
            MATCH (gene:Gene)-[:ENABLES]->(power:Power)
            RETURN gene.name AS Gene, collect(power.name) AS Powers
        """)
        
        print("\nGenes and their Powers:")
        for record in gene_result:
            print(f"{record['Gene']}: {', '.join(record['Powers'])}")



def load_json_data(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    entries = []
    for item in json_data:
        match = re.search(r'\((.*?)\)', item.get('description', ''))    # TODO ?
        realName = match.group(1) if match else item['name']
        entries.append(DataEntry(
            character={"name": item["name"], "realName": realName},
            team={"name": item["team"]},
            genes=[{"name": item["gene"]}] if item["gene"].lower() != "none" else [],
            powers=[{"name": item["power"]}] if item["power"].lower() != "none" else []
        ))
    return entries


def generate_knowledge_graph():
    service = Neo4jService()
    try:
        service.create_graph(load_json_data("models/marvel.json"))
        print("Graph creation completed")
    except Exception as e:
        print(f"Failed to create graph: {e}")
    finally:
        service.close()