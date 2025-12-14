import json

from embeddings.faiss_index import FaissFlatIndex
from embeddings.generator import embed
from embeddings.indexer import EmbeddingIndex
from storage.sqlite_engine import SQLiteEngine


class PensiveDB:
    def __init__(
        self,
        path="pensive.db",
        flush_every: int = 1,
        index_mode="simple",
        enable_cache=True,
    ):
        self.index_mode = index_mode
        self.storage = SQLiteEngine(path, flush_every)

        # detect embedding dimension dynamically
        dim = len(embed("dimension probe"))

        if index_mode == "simple":
            self.index = EmbeddingIndex()
        elif index_mode == "faiss_flat":
            self.index = FaissFlatIndex(dim=dim)
        else:
            raise ValueError("unknown index mode")

        self._load_index()

    def _load_index(self):
        rows = self.storage.conn.execute(
            "SELECT id, embedding FROM embeddings"
        ).fetchall()

        parsed = [(row["id"], row["embedding"]) for row in rows]
        if parsed:
            self.index.build_from_sqlite(parsed)

    def _apply_filters(self, collection, filters):
        """
        return list of document IDs matching structured filters
        """
        rows = self.storage.conn.execute(
            "SELECT id, data FROM documents WHERE collection = ?", (collection,)
        ).fetchall()

        def match(doc, f):
            value = doc.get(f["field"])
            op = f["op"]
            target = f["value"]

            if op == "=":
                return value == target
            if op == "!=":
                return value != target
            if op == ">":
                return value > target
            if op == "<":
                return value < target
            if op == "in":
                return any(t.lower() in str(value).lower() for t in target)
            return False

        matched = []
        for row in rows:
            data = json.loads(row["data"])
            if all(match(data, f) for f in filters):
                matched.append(row["id"])

        return matched

    def query(self, collection, filters=None, semantic_query=None, top_k=5):
        """
        hybrid query (structured filters + semantic ranking)
        """
        candidate_ids = None

        if filters:
            candidate_ids = set(self._apply_filters(collection, filters))

            # valid filters but no matches → return early
            if not candidate_ids:
                return []

        if semantic_query:
            semantic_results = self.search_semantic(
                collection=collection,
                query_text=semantic_query,
                top_k=top_k * 2,
            )

            if candidate_ids is not None:
                semantic_results = [
                    r for r in semantic_results if r["id"] in candidate_ids
                ]

            return semantic_results[:top_k]

        # structured-only query
        if candidate_ids is None:
            return []

        return [self.get(doc_id) for doc_id in candidate_ids]

    def search_semantic(self, collection, query_text, top_k=5):
        query_vec = embed(query_text)

        # NOTE: search runs globally, then filters by collection
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

    def update(self, doc_id, collection, updates: dict):
        updated_data = self.storage.update_document(doc_id, collection, updates)
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
