import json
import sqlite3
import uuid
from datetime import datetime


class SQLiteEngine:
    def __init__(self, path="pensive.db", flush_every: int = 1):
        """
        flush every = 1 -> commits every write
        flush every = 10 -> comits after every 10 writes
        """
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.flush_every = flush_every
        self._pending_writes = 0

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

    """ internal helper for incremental persistence """

    def _bump_writes_and_maybe_flush(self):
        self._pending_writes += 1
        if self.flush_every <= 1:
            # commit every time (default safe behavior)
            self.conn.commit()
            self._pending_writes = 0
        elif self._pending_writes >= self.flush_every:
            self.conn.commit()
            self._pending_writes = 0

    def flush(self):
        """force flush pending writes to disk"""
        if self._pending_writes > 0:
            self.conn.commit()
            self._pending_writes = 0

    def close(self):
        """flush and close the db connection"""
        if self._pending_writes > 0:
            self.flush()
            self.conn.close()

    def __del__(self):
        # best effort flush on gc
        try:
            self.close()
        except Exception:
            pass

    """ insert and fetch (basic crud) """

    def insert_document(self, collection, data_dict):
        doc_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        self.conn.execute(
            "INSERT INTO documents (id, collection, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (doc_id, collection, json.dumps(data_dict), now, now),
        )
        self._bump_writes_and_maybe_flush()

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
        self._bump_writes_and_maybe_flush()

    def update_document(self, doc_id, collection, updates: dict):
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
        self._bump_writes_and_maybe_flush()

        return new_data

    def update_embedding(self, doc_id, vector):
        blob = vector.tobytes()
        self.conn.execute(
            "UPDATE embeddings SET embedding = ? WHERE id = ?", (blob, doc_id)
        )
        self._bump_writes_and_maybe_flush()

    def delete_document(self, doc_id):
        self.conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.execute("DELETE FROM embeddings WHERE id = ?", (doc_id,))
        self._bump_writes_and_maybe_flush()
