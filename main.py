from db import PensiveDB


def main():
    db = PensiveDB()
    doc_id = db.insert(
        "notes",
        {
            "title": "hello world",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec viverra accumsan ante posuere imperdiet. Donec dui enim, blandit interdum pellentesque nec, scelerisque et erat. Donec porttitor sapien nec nisi finibus facilisis. Donec suscipit ante nec eleifend fermentum. Integer bibendum laoreet vulputate. Phasellus sed tristique nunc. Fusce scelerisque mi dui, id scelerisque risus molestie et. Ut aliquam vehicula mi, at lobortis libero viverra non. Integer a accumsan est. In a magna hendrerit, ullamcorper quam nec, vulputate magna. Pellentesque massa ligula, convallis nec metus ut, venenatis interdum sapien. Curabitur luctus ultrices nisi, eu mattis augue interdum placerat. Sed rutrum euismod purus, ut finibus dolor semper eu. Nam cursus velit augue, eget mollis odio ultricies ut. Praesent varius ac ex ac sagittis.",
        },
    )

    print("Inserted:", doc_id)
    print(db.get(doc_id))


if __name__ == "__main__":
    main()
