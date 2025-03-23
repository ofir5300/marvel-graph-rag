from llm.llm import call
from dal.graph_generator import generate_knowledge_graph, query_character
from dotenv import load_dotenv

load_dotenv()

def main():
    generate_knowledge_graph()
    print(query_character("Spider-Man"))
    call("spider-man")

if __name__ == "__main__":
    main() 