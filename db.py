import numpy as np

from embeddings.generator import embed
from embeddings.indexer import EmbeddingIndex
from storage.sqlite_engine import SQLiteEngine


class PensiveDB:
    def __init__(self, path="pensive.db", flush_every: int = 1, enable_cache=True):
        self.storage = SQLiteEngine(path, flush_every)
        self.index = EmbeddingIndex()
        self._load_index()

    def _load_index(self):
        rows = self.storage.conn.execute(
            "SELECT id, embedding FROM embeddings"
        ).fetchall()

        parsed = [(row["id"], row["embedding"]) for row in rows]
        self.index.build_from_sqlite(parsed)

    def search_semantic(self, collection, query_text, top_k=5):
        query_vec = embed(query_text)
        results = self.index.search(query_vec, top_k)

        filtered = []
        for r in results:
            doc = self.get(r["id"])
            if doc and doc["collection"] == collection:
                filtered.append(
                    {"id": r["id"], "score": r["score"], "data": doc["data"]}
                )
        return filtered

    def insert(self, collection, data_dict):
        doc_id = self.storage.insert_document(collection, data_dict)

        text = " ".join(str(v) for v in data_dict.values())

        vector = embed(text)

        self.storage.insert_embedding(doc_id, collection, vector)
        self.index.add(doc_id, vector)

        return doc_id

    def get(self, doc_id):
        return self.storage.get_document(doc_id)

    def update(self, doc_id, updates: dict):
        updated_data = self.storage.update_document(doc_id, updates)
        if not updated_data:
            return None

        text = " ".join(str(v) for v in updated_data.values())

        vector = embed(text)

        self.storage.update_embedding(doc_id, vector)
        self.index.update(doc_id, vector)

        return updated_data

    def delete(self, doc_id):
        self.storage.delete_document(doc_id)
        self.index.remove(doc_id)
        return True

    def close(self):
        self.storage.close()
