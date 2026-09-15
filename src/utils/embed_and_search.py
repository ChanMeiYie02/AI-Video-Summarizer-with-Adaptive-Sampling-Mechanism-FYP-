import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
#../../outputs/transcript.json not found.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "outputs", "transcript.json")
EMBEDDINGS_SAVE_PATH = os.path.join(BASE_DIR, "outputs", "embeddings.npy")

def embed_and_search():
    print("1. Loading Transcript Data...")
    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"Error: {TRANSCRIPT_PATH} not found.")
        return
        
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract text content for each chunk
    texts = [item['text'] for item in data]
    print(f"Loaded {len(texts)} chunks of text/context.")

    # 2. Embedding Process
    print("\n2. Initializing Embedding Model (fast, real-time capable)...")
    # Using a lightweight, very fast embedding model. 
    # For better semantic search, you can use 'BAAI/bge-small-en-v1.5'
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda') 
    
    print("Generating embeddings...")
    embeddings = model.encode(texts)
    
    # 3. Save the Embedding values
    print(f"\n3. Saving embeddings to {EMBEDDINGS_SAVE_PATH}...")
    np.save(EMBEDDINGS_SAVE_PATH, embeddings)
    print("Embeddings saved successfully! You can reuse them for search or clustering later without recalculating.")

    # 4. Search feature demonstration (using the same embeddings)
    print("\n--- Testing Vector Search ---")
    query = "How to record a slideshow through powerpoint?"
    print(f"Search Query: '{query}'")
    
    query_embedding = model.encode([query])
    
    # Calculate Cosine Similarity between query and all saved embeddings
    similarities = cosine_similarity(query_embedding, embeddings)[0]  # type: ignore[arg-type]
    
    # Get top 2 most relevant chunks
    top_indices = np.argsort(similarities)[::-1][:2]
    
    for i, idx in enumerate(top_indices):
        print(f"\nTop {i+1} Match (Score: {similarities[idx]:.4f}):")
        print(texts[idx][:200] + "...")

if __name__ == "__main__":
    embed_and_search()
