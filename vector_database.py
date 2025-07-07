import faiss
import numpy as np
import os
import pickle

VECTOR_DIM = 768  # Set according to your embedding size
FAISS_INDEX_FILE = 'vector.index'
CHUNKS_FILE = 'chunks.pkl'

class VectorDatabase:
    def __init__(self, dim=VECTOR_DIM):
        self.index = faiss.IndexFlatIP(dim)  # Inner Product for Cosine Similarity (with normalized vectors)
        self.chunks = []  # Stores text chunks in same order as vectors

    def add(self, chunk, embedding):
        embedding = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return  # Skip invalid embeddings
        embedding /= norm  # Normalize for cosine similarity
        self.index.add(embedding.reshape(1, -1))
        self.chunks.append(chunk)

    def search(self, query_embedding, top_n=3):
        embedding = np.array(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return []
        embedding /= norm
        D, I = self.index.search(embedding.reshape(1, -1), top_n)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], score))
        return results

    def save(self):
        faiss.write_index(self.index, FAISS_INDEX_FILE)
        with open(CHUNKS_FILE, 'wb') as f:
            pickle.dump(self.chunks, f)

    def load(self):
        if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(CHUNKS_FILE):
            self.index = faiss.read_index(FAISS_INDEX_FILE)
            with open(CHUNKS_FILE, 'rb') as f:
                self.chunks = pickle.load(f)
            print(f'Loaded {len(self.chunks)} chunks from saved vector database')
        else:
            print('No saved vector database found. Starting fresh.')
