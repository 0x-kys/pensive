import os
import sys

from db import PensiveDB

DB_PATH = "pensive.db"

BIG_TEXT = """
Artificial intelligence is transforming software development. Modern systems can now generate code, review pull requests, and even suggest architectural improvements. Teams that adopt AI tools report faster development cycles and fewer bugs in production. The challenge, however, is integrating these tools responsibly without creating over-reliance.

Cooking at home has seen a resurgence as people look for healthier alternatives to fast food. Simple meals like stir-fries, soups, and roasted vegetables require minimal ingredients but deliver strong nutritional value. Many beginners start with basic knife skills and gradually experiment with herbs, spices, and different cuisines.

Electric vehicles are becoming increasingly popular as battery technology improves and charging networks expand. Companies are pushing for longer ranges and faster charging times. Governments around the world are offering incentives to reduce carbon emissions and accelerate the shift away from fossil fuels.

Traveling to new countries exposes people to unfamiliar cultures and perspectives. Exploring local food, music, and traditions helps visitors build a deeper appreciation for diversity. Many travelers also enjoy documenting their journeys through photography and writing.

Good mental health requires consistent habits such as regular exercise, proper sleep, social interactions, and mindfulness. Small daily practices like journaling or walking outdoors can significantly reduce stress levels. Experts encourage people to treat mental well-being with the same priority as physical health.
"""


def split_paragraphs(text: str):
    return [p.strip() for p in text.strip().split("\n\n") if p.strip()]


def pretty_print_semantic_results(results):
    print("\nSemantic Search Results:")
    for i, r in enumerate(results, start=1):
        print(f"\nResult #{i}")
        print(f"  ID: {r['id']}")
        print(f"  Score: {r['score']:.4f}")
        print(f"  Title: {r['data']['title']}")
        print(f"  Content (preview): {r['data']['content'][:120]}...")


def cmd_add():
    db = PensiveDB(
        path=DB_PATH,
        flush_every=10,
        index_mode="faiss_flat",
    )

    paragraphs = split_paragraphs(BIG_TEXT)
    print(f"Found {len(paragraphs)} paragraphs.")
    print("--- INSERTING NOTES ---")

    for idx, para in enumerate(paragraphs, start=1):
        doc_id = db.insert(
            "notes",
            {"title": f"Paragraph {idx}", "content": para},
        )
        print(f"Inserted note {idx}: {doc_id}")

    db.close()
    print("\nInsert complete.")


def cmd_search():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run `add` first.")
        return

    db = PensiveDB(
        path=DB_PATH,
        index_mode="faiss_flat",
    )

    results = db.query(
        "notes",
        filters=[
            {
                "field": "content",
                "op": "in",
                "value": [
                    "mental",
                    "health",
                ],
            }
        ],
        semantic_query="mindfulness",
        top_k=3,
    )

    pretty_print_semantic_results(results)

    db.close()


def cmd_clean():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Database deleted.")
    else:
        print("No database found.")


def print_help():
    print(
        """
Usage:
  uv run cli.py add     # insert demo documents
  uv run cli.py search  # run semantic search
  uv run cli.py clean   # delete database
"""
    )


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    if cmd == "add":
        cmd_add()
    elif cmd == "search":
        cmd_search()
    elif cmd == "clean":
        cmd_clean()
    else:
        print(f"Unknown command: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
