import numpy as np

from embeddings.generator import embed
from storage.sqlite_engine import SQLiteEngine


class PensiveDB:
    def __init__(self, path="pensive.db"):
        self.storage = SQLiteEngine(path)

    def insert(self, collection, data_dict):
        doc_id = self.storage.insert_document(collection, data_dict)

        text = " ".join(str(v) for v in data_dict.values())

        vector = embed(text)

        self.storage.insert_embedding(doc_id, collection, vector)

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

        return updated_data

    def delete(self, doc_id):
        self.storage.delete_document(doc_id)
        return True
