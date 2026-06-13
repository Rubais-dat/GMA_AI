import os
import csv
import torch
from transformers import AutoTokenizer, AutoModel

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
CLEANED_FILE = "data/gma_cleaned.txt"
EMBEDDINGS_FILE = "data/gma_embeddings_local.csv"

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.squeeze().tolist()

if __name__ == "__main__":
    # Read cleaned text
    if not os.path.exists(CLEANED_FILE):
        raise FileNotFoundError(f"Cleaned database file not found: {CLEANED_FILE}")
        
    with open(CLEANED_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Smart paragraph-based chunking
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # If adding this paragraph exceeds CHUNK_SIZE, store the current chunk and start a new one
        if len(current_chunk) + len(para) + 2 > CHUNK_SIZE:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Start new chunk
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
                
    # Add any remaining text
    if current_chunk:
        chunks.append(current_chunk.strip())

    print(f"Text length: {len(text)} characters. Created {len(chunks)} chunks.")

    # Generate embeddings
    print("Generating embeddings for all chunks...")
    embeddings = []
    for idx, chunk in enumerate(chunks):
        vec = embed_text(chunk)
        embeddings.append(vec)
        if (idx + 1) % 10 == 0 or idx + 1 == len(chunks):
            print(f"Processed {idx + 1}/{len(chunks)} chunks.")

    # Save embeddings
    os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)
    with open(EMBEDDINGS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chunk_id", "chunk_text", "embedding"])
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            writer.writerow([i, chunk, vector])

    print(f"Total chunks: {len(chunks)}")
    print(f"Embeddings saved successfully to {EMBEDDINGS_FILE}")
