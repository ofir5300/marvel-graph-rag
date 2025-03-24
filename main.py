from dal.redis import RedisService, test_embedder
from dal.loaders import run_all_ETLs
from dotenv import load_dotenv

from llm.embeddings import Embedder

load_dotenv()

def main():
    # generate_knowledge_graph()
    # RedisService().reset_index()
    run_all_ETLs()
    embedder = Embedder()
    res = embedder.query_similar("welverin?")
    print(res)
    # test_embedder()
    # character = query_character("Spider-Man")
    # print(character)
    # call("who is welveri") #  TODO make it sucess
    # call("tell me about spider guy")
if __name__ == "__main__":
    main() 