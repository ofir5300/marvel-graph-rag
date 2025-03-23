from llm.llm import call
from dal.graph_generator import generate_knowledge_graph, query_character
from dotenv import load_dotenv

load_dotenv()

def main():
    generate_knowledge_graph()
    
    # todo make this work:
    print(query_character("Spider-Man"))
    call("What is the capital of France?")

if __name__ == "__main__":
    main() 