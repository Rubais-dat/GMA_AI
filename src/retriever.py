import os
import csv
import faiss
import json
import numpy as np

class Retriever:
    def __init__(self, embeddings_file="data/gma_embeddings_local.csv"):
        self.embeddings_file = embeddings_file
        self.chunks = []
        self.vectors = []
        self.index = None
        self._load_embeddings()
        self._build_index()

    def _load_embeddings(self):
        if not os.path.exists(self.embeddings_file):
            raise FileNotFoundError(f"Embeddings file not found: {self.embeddings_file}")
        with open(self.embeddings_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.chunks.append(row["chunk_text"])
                vector = np.array(json.loads(row["embedding"]), dtype=np.float32)
                self.vectors.append(vector)
        self.vectors = np.array(self.vectors, dtype=np.float32)
        print(f"Total chunks loaded: {len(self.chunks)}")

    def _build_index(self):
        dim = self.vectors.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.vectors)
        print(f"FAISS index built with {self.vectors.shape[0]} vectors.")

    def retrieve(self, query_vector, top_k=5):
        query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            results.append({"text": self.chunks[idx], "score": float(dist)})
        return results
