from llm.llm import call
from dal.graph_generator import generate_knowledge_graph
from dotenv import load_dotenv

load_dotenv()

def main():
    generate_knowledge_graph()
    call("What is the capital of France?")

if __name__ == "__main__":
    main() 