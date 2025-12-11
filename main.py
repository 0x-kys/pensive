from db import PensiveDB

BIG_TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec viverra accumsan ante posuere imperdiet. Donec dui enim, blandit interdum pellentesque nec, scelerisque et erat. Donec porttitor sapien nec nisi finibus facilisis. Donec suscipit ante nec eleifend fermentum. Integer bibendum laoreet vulputate. Phasellus sed tristique nunc. Fusce scelerisque mi dui, id scelerisque risus molestie et. Ut aliquam vehicula mi, at lobortis libero viverra non. Integer a accumsan est. In a magna hendrerit, ullamcorper quam nec, vulputate magna. Pellentesque massa ligula, convallis nec metus ut, venenatis interdum sapien. Curabitur luctus ultrices nisi, eu mattis augue interdum placerat. Sed rutrum euismod purus, ut finibus dolor semper eu. Nam cursus velit augue, eget mollis odio ultricies ut. Praesent varius ac ex ac sagittis.

Etiam efficitur faucibus leo vel bibendum. Nullam at ante vel augue iaculis tincidunt. Nam volutpat sollicitudin interdum. Ut vel neque nisi. Duis eget ipsum eu risus eleifend efficitur ut ac ligula. Aenean luctus vestibulum odio non rhoncus. Sed tempus, quam vel commodo condimentum, dui magna efficitur elit, eget fermentum lectus leo sed ipsum. Pellentesque tellus nisi, dictum sit amet ante eget, tempor bibendum magna. Maecenas quis elementum ante. Ut sit amet massa pretium, accumsan eros eu, ornare tellus. Duis eu eleifend tellus, in fringilla magna. Aliquam sit amet ex hendrerit, hendrerit ipsum et, tincidunt sem.

Fusce augue enim, fringilla at pulvinar rutrum, laoreet eget dui. Proin luctus enim semper finibus tristique. Ut blandit eros sit amet vehicula commodo. Sed dignissim lacinia massa quis molestie. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc et sollicitudin justo. Cras efficitur, purus et tristique dictum, nunc augue pharetra erat, nec tristique sapien ipsum a purus. Proin molestie consectetur ligula, vel dapibus justo volutpat sed. Pellentesque odio purus, efficitur mattis quam sed, rhoncus facilisis quam. Suspendisse nec diam eu lorem dapibus volutpat sit amet vitae mauris.

Maecenas lacinia ante at malesuada eleifend. Aliquam erat volutpat. Cras pulvinar accumsan dui eget varius. Cras et rutrum lectus, sed mollis magna. Curabitur quis commodo metus. Nunc pharetra arcu in turpis mattis, tincidunt eleifend urna blandit. Phasellus rutrum est lacinia mattis rhoncus. Maecenas iaculis quis augue et pretium. Pellentesque suscipit rhoncus ex eu cursus. Aliquam erat volutpat. In feugiat ex vel diam elementum tincidunt id at lacus. Duis eu auctor quam. Nam vitae tristique ex.

Cras posuere nisl imperdiet, tempus lectus in, luctus mi. Aenean vestibulum pellentesque risus, at molestie erat consectetur ac. Aliquam erat volutpat. Duis malesuada ipsum semper leo lacinia interdum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed vel malesuada tortor. Phasellus mattis turpis nibh, non suscipit arcu venenatis ac. Aenean a metus ut arcu faucibus porttitor. Morbi vitae diam et ante porttitor porttitor id ut velit. Proin non ex maximus eros vehicula efficitur.
"""


def split_paragraphs(text: str):
    """Split into paragraphs based on blank lines."""
    return [p.strip() for p in text.strip().split("\n\n") if p.strip()]


def main():
    db = PensiveDB(path="pensive.db", flush_every=10)

    paragraphs = split_paragraphs(BIG_TEXT)

    print(f"Found {len(paragraphs)} paragraphs.")
    print("--- INSERTING NOTES ---")

    ids = []
    for idx, para in enumerate(paragraphs, start=1):
        doc_id = db.insert(
            "notes",
            {"title": f"Paragraph {idx}", "content": para},
        )
        ids.append(doc_id)
        print(f"Inserted note {idx}: {doc_id}")

    print("\n--- FETCHING INSERTED NOTES ---")
    for doc_id in ids:
        doc = db.get(doc_id)
        print(f"{doc_id} => title: {doc['data']['title']}")

    db.close()
    print("\nDB flushed & closed!")


if __name__ == "__main__":
    main()
