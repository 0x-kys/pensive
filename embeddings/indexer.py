import numpy as np


class EmbeddingIndex:
    def __init__(self):
        self.ids = []
        self.vectors = []

    def add(self, doc_id, vector):
        vector = vector.astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return
        vector = vector / norm

        self.ids.append(doc_id)
        self.vectors.append(vector)

    def update(self, doc_id, vector):
        vector = vector.astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return
        vector = vector / norm

        for i, id_ in enumerate(self.ids):
            if id_ == doc_id:
                self.vectors[i] = vector
                return

        self.add(doc_id, vector)

    def remove(self, doc_id):
        for i, id_ in enumerate(self.ids):
            if id_ == doc_id:
                self.ids.pop(i)
                self.vectors.pop(i)
                return

    def build_from_sqlite(self, rows):
        self.ids = []
        self.vectors = []

        for doc_id, blob in rows:
            vec = np.frombuffer(blob, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue
            vec = vec / norm
            self.ids.append(doc_id)
            self.vectors.append(vec)

    def search(self, query_vector, top_k=5):
        if not self.ids:
            return []

        query = query_vector.astype(np.float32)
        norm = np.linalg.norm(query)
        if norm == 0:
            return []
        query = query / norm

        matrix = np.vstack(self.vectors)

        # cosine similarity
        scores = np.dot(matrix, query)

        top_indices = np.argsort(scores)[-top_k:][::-1]

        return [{"id": self.ids[i], "score": float(scores[i])} for i in top_indices]
