from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_core.documents import Document
import numpy as np
from typing import List, Optional, Tuple
import os

class Embedder:
    embedder: OpenAIEmbeddings
    vectorstore: RedisVectorStore
    index: str

    def __init__(self, index: str = os.getenv("REDIS_INDEX")):
        self.embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        self.index = index
        config = RedisConfig(
            index_name=index,
            distance_metric="COSINE"
        )
        self.vectorstore = RedisVectorStore(embeddings=self.embedder, config=config)

    def store_embedding(self, text: str, doc_id: str) -> None:
        self.vectorstore.add_texts([text], metadatas=[{"id": doc_id}])

    def query_similar(self, query: str, k: int = 2) -> List[dict]:
        docs: List[Tuple[Document, float]] = self.vectorstore.similarity_search_with_score(query, k=k)
        return [{"text": doc[0].page_content, "score": doc[1]} for doc in docs]

    def bulk_embed(self, texts: List[str], doc_ids: Optional[List[str]] = None) -> None:
        if doc_ids is None:
            doc_ids = [f"doc:{i}" for i in range(len(texts))]
        metadatas = [{"id": doc_id} for doc_id in doc_ids]
        res = self.vectorstore.add_texts(texts, metadatas=metadatas)
        print(res)