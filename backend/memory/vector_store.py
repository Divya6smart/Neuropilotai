import os

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("[Memory] Warning: chromadb not found. Falling back to MockMemory.")

class MockMemory:
    def store(self, text, metadata=None):
        print(f"[MockMemory] Storing: {text[:50]}...")
    def query(self, text, n_results=3):
        return {"documents": [[]]}

class VectorMemory:
    def __init__(self, collection_name="neuropilot_memory"):
        if not CHROMA_AVAILABLE:
            self.client = None
            self.collection = MockMemory()
            return

        try:
            self.client = chromadb.PersistentClient(path="./data/chroma")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
        except Exception as e:
            print(f"[Memory] Error initializing ChromaDB: {e}")
            self.collection = MockMemory()

    def store(self, text: str, metadata: dict = None):
        if not CHROMA_AVAILABLE:
            self.collection.store(text, metadata)
            return
        
        doc_id = str(hash(text))
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

memory = VectorMemory()
