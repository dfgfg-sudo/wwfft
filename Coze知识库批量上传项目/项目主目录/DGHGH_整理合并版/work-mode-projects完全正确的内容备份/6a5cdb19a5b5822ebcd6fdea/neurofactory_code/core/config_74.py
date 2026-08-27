import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List

class QuantumMemory:
    def __init__(self, config):
        self.config = config
        self.dim = 768
        self.index = faiss.IndexFlatL2(self.dim)
        self.memory_db = []
        # 使用轻量嵌入模型
        try:
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        except:
            self.encoder = None
            print("警告：sentence-transformers未安装，将使用随机向量")

    def store(self, text: str):
        vec = self._text_to_vector(text)
        self.index.add(np.array([vec]))
        self.memory_db.append(text)

    def retrieve(self, query: str, k=3) -> List[str]:
        query_vec = self._text_to_vector(query)
        distances, indices = self.index.search(np.array([query_vec]), k)
        results = []
        for i in indices[0]:
            if i < len(self.memory_db):
                results.append(self.memory_db[i])
        return results

    def _text_to_vector(self, text: str) -> np.ndarray:
        if self.encoder:
            return self.encoder.encode([text])[0].astype('float32')
        else:
            # fallback: 随机向量
            return np.random.randn(self.dim).astype('float32')