import json
import sqlite3
import uuid
from datetime import datetime


class SQLiteEngine:
    def __init__(self, path="pensive.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    """ storage system """

    def _init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            collection TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            collection TEXT NOT NULL,
            embedding BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)
        self.conn.commit()

    """ insert and fetch (basic crud) """

    def insert_document(self, collection, data_dict):
        doc_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        self.conn.execute(
            "INSERT INTO documents (id, collection, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (doc_id, collection, json.dumps(data_dict), now, now),
        )
        self.conn.commit()

        return doc_id

    def get_document(self, doc_id):
        row = self.conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()

        if row:
            row = dict(row)
            row["data"] = json.loads(row["data"])

        return row

    def insert_embedding(self, doc_id, collection, vec):
        blob = vec.tobytes()
        self.conn.execute(
            "INSERT INTO embeddings (id, collection, embedding) VALUES (?, ?, ?)",
            (doc_id, collection, blob),
        )
        self.conn.commit()

    def update_document(self, doc_id, updates: dict):
        row = self.get_document(doc_id)
        if not row:
            return None

        new_data = row["data"]
        new_data.update(updates)

        now = datetime.now().isoformat()

        self.conn.execute(
            "UPDATE documents SET data = ?, updated_at = ? WHERE id = ?",
            (json.dumps(new_data), now, doc_id),
        )
        self.conn.commit()

        return new_data

    def update_embedding(self, doc_id, vector):
        blob = vector.tobytes()
        self.conn.execute(
            "UPDATE embeddings SET embedding = ? WHERE id = ?", (blob, doc_id)
        )
        self.conn.commit()

    def delete_document(self, doc_id):
        self.conn.execute("DELETE FROM documents WHERE id = ?", (doc_id))
        self.conn.execute("DELETE FROM embeddings WHERE id = ?", (doc_id))
        self.conn.commit()
