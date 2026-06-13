import os
import csv
import faiss
import json
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer


EMBEDDINGS_FILE = "data/HR_policy_embeddings_local.csv"
CACHE_FILE = "data/query_cache.json"
TOP_K = 5  # top results for re-ranking


chunks = []
vectors = []

if not os.path.exists(EMBEDDINGS_FILE):
    raise FileNotFoundError(f"Embeddings file not found: {EMBEDDINGS_FILE}")

with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        chunks.append(row["chunk_text"])
        vec = np.array(json.loads(row["embedding"]), dtype="float32")
        vectors.append(vec)

vectors = np.vstack(vectors).astype("float32")
print(f"Total chunks loaded: {len(chunks)}")


dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)
print(f"FAISS index built with {index.ntotal} vectors.")


vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(chunks)

def re_rank(query_vec, top_indices):
    query_tfidf = vectorizer.transform([query_vec])
    sims = (query_tfidf @ tfidf_matrix[top_indices].T).toarray()[0]
    ranked_indices = [top_indices[i] for i in np.argsort(-sims)]
    return ranked_indices, sims[np.argsort(-sims)]


cache = {}
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cache, f)

print(f"Cache initialized at {CACHE_FILE}")


print(f"Indexing complete. {len(chunks)} chunks are ready for retrieval.")
print(f"FAISS vectors dimension: {dimension}")
print("No query required in this run. Script finished successfully.")
