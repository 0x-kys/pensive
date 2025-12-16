import os
from typing import List, Optional

import typer

from db import PensiveDB

app = typer.Typer(help="PensiveDB — local-first semantic database")

DEFAULT_DB_PATH = "pensive.db"


# -------------------------
# Utility
# -------------------------


def ensure_db_exists(path: str):
    if not os.path.exists(path):
        typer.echo("Database not found. Run `pensive init` first.")
        raise typer.Exit(code=1)


def read_file(path: str) -> str:
    if not os.path.exists(path):
        typer.echo(f"File not found: {path}")
        raise typer.Exit(code=1)

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------
# Commands
# -------------------------


@app.command()
def init(
    db_path: str = typer.Option(
        DEFAULT_DB_PATH,
        help="Path to create the database",
    ),
):
    """
    Initialize a new PensiveDB database.
    """
    if os.path.exists(db_path):
        typer.echo("Database already exists.")
        return

    db = PensiveDB(
        path=db_path,
        index_mode="faiss_flat",
    )
    db.close()

    typer.echo(f"Initialized database at {db_path}")


@app.command()
def add(
    file: str = typer.Argument(..., help="Path to text file to ingest"),
    collection: str = typer.Option(
        "notes",
        help="Collection name",
    ),
    db_path: str = typer.Option(
        DEFAULT_DB_PATH,
        help="Path to database file",
    ),
):
    """
    Add a file to the database.
    """
    ensure_db_exists(db_path)

    content = read_file(file)

    db = PensiveDB(
        path=db_path,
        flush_every=10,
        index_mode="faiss_flat",
    )

    doc_id = db.insert(
        collection,
        {
            "title": os.path.basename(file),
            "content": content,
        },
    )

    db.close()
    typer.echo(f"Inserted document {doc_id} into '{collection}'")


@app.command()
def search(
    query: str = typer.Argument(..., help="Semantic search query"),
    collection: str = typer.Option(
        "notes",
        help="Collection name",
    ),
    filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Keyword filter (can be repeated)",
    ),
    top_k: int = typer.Option(
        5,
        help="Number of results to return",
    ),
    db_path: str = typer.Option(
        DEFAULT_DB_PATH,
        help="Path to database file",
    ),
):
    """
    Run a semantic search with optional keyword filters.
    """
    ensure_db_exists(db_path)

    filters = None
    if filter:
        filters = [
            {
                "field": "content",
                "op": "in",
                "value": filter,
            }
        ]

    db = PensiveDB(
        path=db_path,
        index_mode="faiss_flat",
    )

    results = db.query(
        collection=collection,
        filters=filters,
        semantic_query=query,
        top_k=top_k,
    )

    if not results:
        typer.echo("No results found.")
        return

    typer.echo("\nSemantic Search Results:")
    for i, r in enumerate(results, start=1):
        typer.echo(f"\nResult #{i}")
        typer.echo(f"  ID: {r['id']}")
        typer.echo(f"  Score: {r['score']:.4f}")
        typer.echo(f"  Title: {r['data']['title']}")
        typer.echo(f"  Content (preview): {r['data']['content'][:120]}...")

    db.close()


@app.command()
def clean(
    db_path: str = typer.Option(
        DEFAULT_DB_PATH,
        help="Path to database file",
    ),
):
    """
    Delete the database.
    """
    if os.path.exists(db_path):
        os.remove(db_path)
        typer.echo("Database deleted.")
    else:
        typer.echo("No database found.")


# -------------------------
# Entry
# -------------------------

if __name__ == "__main__":
    app()
