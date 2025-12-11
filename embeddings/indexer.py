import numpy as np


class EmbeddingIndex:
    def __init__(self):
        self.ids = []  # list[str]
        self.vectors = []  # list[np.ndarray]

    def add(self, doc_id, vector):
        self.ids.append(doc_id)
        self.vectors.append(vector)

    def update(self, doc_id, vector):
        for i, id_ in enumerate(self.ids):
            if id_ == doc_id:
                self.vectors[i] = vector
                return
        # if not found... treat as insert
        self.add(doc_id, vector)

    def remove(self, doc_id):
        for i, id_ in enumerate(self.ids):
            if id_ == doc_id:
                self.ids.pop(i)
                self.vectors.pop(i)
                return

    def build_from_sqlite(self, rows):
        """
        rows = [(id, embedding_bytes), ...]
        """
        for doc_id, blob in rows:
            vec = np.frombuffer(blob, dtype=np.float32)
            self.add(doc_id, vec)

    def search(self, query_vector, top_k=5):
        if len(self.ids) == 0:
            return []

        # convert vectors into 2D numpy array
        matrix = np.vstack(self.vectors)
        query = query_vector / np.linalg.norm(query_vector)
        matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)

        # cosine similarity = dot product of normalized vectors
        scores = np.dot(matrix_norm, query)

        # top-k results
        top_indices = np.argsort(scores)[-top_k:][::-1]

        score_results = []
        for idx in top_indices:
            score_results.append({"id": self.ids[idx], "score": float(scores[idx])})
        return score_results
