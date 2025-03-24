import os
import redis
from typing import Optional

from llm.embeddings import Embedder

class RedisService:
    def __init__(self, index: Optional[str] = os.getenv("REDIS_INDEX")):
        self.redis_url = os.getenv("REDIS_URL")
        self.index = index
        self.client = redis.from_url(self.redis_url)
        self.client.ping()

    def delete_index(self) -> None:
        try:
            self.client.execute_command('FT.DROPINDEX', self.index)
            print(f"Successfully dropped index: {self.index}")
        except Exception as e:
            print(f"Error dropping index: {e}")

    def create_index(self) -> None:
        try:
            self.client.execute_command(
                'FT.CREATE', self.index, 'ON', 'HASH', 'PREFIX', '1', 'doc:',
                'SCHEMA', 'text', 'TEXT',
                'embedding', 'VECTOR', 'FLAT', '6', 'TYPE', 'FLOAT32', 'DIM', '1536',
                'DISTANCE_METRIC', 'COSINE'
            )
            print(f"Successfully created index: {self.index}")
        except Exception as e:
            print("Index might already exist:", e)

    def reset_index(self) -> None:
        """Delete and recreate the index"""
        self.delete_index()
        self.create_index()

#  TODO should remove?

def test_embedder():
    embedder = Embedder()
    embedder.bulk_embed(["Hello, world!", "This is a test.", "the most important this is the world is tupac"])
    res = embedder.query_similar("what is the most important thing?")
    print(res)