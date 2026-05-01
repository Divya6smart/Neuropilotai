import chromadb
from chromadb.utils import embedding_functions
import os

class VectorMemory:
    def __init__(self, collection_name="neuropilot_memory"):
        self.client = chromadb.PersistentClient(path="./data/chroma")
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def store(self, text: str, metadata: dict = None):
        # Generate a simple ID
        doc_id = str(hash(text))
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

memory = VectorMemory()
