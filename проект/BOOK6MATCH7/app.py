from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "books.json"

GENRES = ["Драма", "Комедия", "Приключения", "Ужасы (хоррор)"]
PREFERENCES = [
    "Захватывающий сюжет",
    "Лёгкое чтение",
    "Глубокий смысл",
    "Много приключений",
]


def load_books():
    """Load and validate the catalogue from data/books.json."""
    with DATA_FILE.open(encoding="utf-8") as file:
        books = json.load(file)
    if not isinstance(books, list):
        raise ValueError("Каталог книг должен быть списком")
    # Be defensive: malformed records should not crash the whole catalogue.
    valid = []
    for book in books:
        if not isinstance(book, dict) or not book.get("title") or not book.get("author"):
            continue
        try:
            book["pages"] = int(book.get("pages", 200))
        except (TypeError, ValueError):
            book["pages"] = 200
        book.setdefault("genre", "Драма")
        book.setdefault("preferences", [])
        if not isinstance(book["preferences"], list):
            book["preferences"] = []
        book.setdefault("description", "")
        valid.append(book)
    return valid


def filter_books(genre="", max_pages="", preference=""):
    books = load_books()
    genre = (genre or "").strip()
    preference = (preference or "").strip()
    try:
        page_limit = int(max_pages) if str(max_pages).strip() else None
    except (TypeError, ValueError):
        page_limit = None

    result = []
    for book in books:
        if genre and genre != "Любой жанр" and book["genre"].casefold() != genre.casefold():
            continue
        if page_limit is not None and book["pages"] > page_limit:
            continue
        if preference and preference != "Не важно":
            book_preferences = [str(item).casefold() for item in book["preferences"]]
            if preference.casefold() not in book_preferences:
                continue
        result.append(book)
    return result


@app.get("/")
def index():
    return render_template(
        "index.html",
        genres=GENRES,
        preferences=PREFERENCES,
        total=len(load_books()),
    )


@app.post("/api/search")
def api_search():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = request.form
    results = filter_books(
        genre=payload.get("genre", ""),
        max_pages=payload.get("max_pages", ""),
        preference=payload.get("preference", ""),
    )
    return jsonify({"count": len(results), "books": results})


@app.get("/api/books")
def api_books():
    books = load_books()
    return jsonify({"count": len(books), "books": books, "genres": GENRES})


@app.get("/health")
def health():
    books = load_books()
    return jsonify({"status": "ok", "books": len(books)})


if __name__ == "__main__":
    app.run(debug=True)
