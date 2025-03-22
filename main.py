from configuration.graph_generator import Neo4jService, DataEntry
import json, re

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


def main():
    service = Neo4jService()
    try:
        service.create_graph(load_json_data("data/marvel.json"))
        print("Graph creation completed")
    except Exception as e:
        print(f"Failed to create graph: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    main() 