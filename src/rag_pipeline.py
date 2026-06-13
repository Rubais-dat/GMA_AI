from retriever import Retriever
from embedding import embed_text 

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()

    def run(self, query, top_k=5):
        # Generate embedding for query
        query_vec = embed_text(query)
        # Retrieve top chunks
        top_results = self.retriever.retrieve(query_vec, top_k=top_k)
        return top_results
