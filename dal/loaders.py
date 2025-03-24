import json
from typing import List

from dal.graph_generator import Neo4jService
from llm.embeddings import Embedder
from models.types import InformationDataEntry, RelationalDataEntry



def extract_and_transform_relational_data(file_path: str) -> List[RelationalDataEntry]:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    entries = []
    for item in json_data:
        entries.append(RelationalDataEntry(
            character=item["name"].lower(),
            team=item["team"].lower(),
            gene=item["gene"].lower(),
            power=item["power"].lower()
        ))
    return entries

def extract_and_transform_information_data(file_path: str) -> List[InformationDataEntry]:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    entries = []
    for item in json_data:
        entries.append(InformationDataEntry(
            character=item["name"].lower(),
            text=item["text"].lower()
        ))
    return entries

def generate_knowledge_graph():
    service = Neo4jService()
    try:
        data = extract_and_transform_relational_data("models/marvel_relations.json")
        service.create_graph(data)
        print("Graph creation completed")
    except Exception as e:
        print(f"Failed to create graph: {e}")
    finally:
        service.close()

def generate_information_embeddings():
    service = Embedder()
    data = extract_and_transform_information_data("models/marvel_information.json")
    texts = [entry.text for entry in data]
    doc_ids = [f"character:{entry.character}" for entry in data]
    service.bulk_embed(texts, doc_ids)

def run_all_ETLs():
    generate_knowledge_graph()
    generate_information_embeddings()
