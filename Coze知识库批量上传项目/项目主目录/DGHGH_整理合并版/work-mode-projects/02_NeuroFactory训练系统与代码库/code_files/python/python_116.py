import faiss
import numpy as np

class AutonomousMemory:
    def __init__(self, dim=768):
        self.index = faiss.IndexFlatL2(dim)
        self.memory = []

    def add(self, embedding, metadata):
        self.memory.append({'embedding': embedding, 'metadata': metadata})
        self.index.add(np.array([embedding]).astype('float32'))

    def retrieve(self, query_emb, k=5):
        distances, indices = self.index.search(np.array([query_emb]).astype('float32'), k)
        return [self.memory[i] for i in indices[0] if i < len(self.memory)]