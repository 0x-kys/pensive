import faiss
import numpy as np


class FaissFlatIndex:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # inner product = cosine similarity
        self.ids = []
        self._vec_store = []  # track vectors manually

    def add(self, doc_id, vector):
        vector = vector.astype(np.float32)
        vector = vector / np.linalg.norm(vector)

        self.index.add(vector[np.newaxis, :])  # type: ignore[arg-type]
        self.ids.append(doc_id)
        self._vec_store.append(vector)

    def update(self, doc_id, vector):
        self.remove(doc_id)
        self.add(doc_id, vector)

    def remove(self, doc_id):
        if doc_id not in self.ids:
            return

        idx = self.ids.index(doc_id)
        self.ids.pop(idx)
        self._vec_store.pop(idx)

        self.rebuild()

    def rebuild(self):
        self.index = faiss.IndexFlatIP(self.dim)

        if len(self._vec_store) == 0:
            return

        matrix = np.vstack(self._vec_store).astype(np.float32)
        self.index.add(matrix)  # type: ignore[arg-type]

    def build_from_sqlite(self, rows):
        self.ids = []
        self._vec_store = []
        self.index = faiss.IndexFlatIP(self.dim)

        for doc_id, blob in rows:
            vec = np.frombuffer(blob, dtype=np.float32)
            vec = vec / np.linalg.norm(vec)

            self.ids.append(doc_id)
            self._vec_store.append(vec)

        if len(self._vec_store) > 0:
            matrix = np.vstack(self._vec_store).astype(np.float32)
            self.index.add(matrix)  # type: ignore[arg-type]

    def search(self, query_vector, top_k=5):
        if len(self.ids) == 0:
            return []

        q = query_vector.astype(np.float32)
        q = q / np.linalg.norm(q)
        q = q[np.newaxis, :]

        scores, indices = self.index.search(q, top_k)  # type: ignore[misc]

        scores = scores[0]
        indices = indices[0]

        results = []
        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            results.append({"id": self.ids[idx], "score": float(score)})
        return results
