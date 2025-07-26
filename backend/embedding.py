from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# Load multilingual embedding model
model = SentenceTransformer("intfloat/multilingual-e5-small")  # Good Bengali support

# Embed your cleaned & chunked text
def embed_chunks(chunks):
    return model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)



def store_embeddings(chunks, embeddings):
    """
    Store chunk embeddings in a FAISS index.
    Args:
        chunks (list): List of text chunks.
        embeddings (np.ndarray): Embeddings of chunks.
    Returns:
        tuple: (FAISS index, chunks)
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # cosine similarity distance IndexFlatIP (can use IndexFlatL2 for l2 similarity)
    index.add(embeddings)
    return index, chunks