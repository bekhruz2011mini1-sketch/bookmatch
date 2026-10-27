import unittest
from app import app, load_books, GENRES


class Book6Match7Tests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BOOK6MATCH7", response.data)

    def test_catalog_is_large_and_uses_four_genres(self):
        books = load_books()
        self.assertGreaterEqual(len(books), 400)
        self.assertEqual(set(book["genre"] for book in books), set(GENRES))

    def test_books_api(self):
        response = self.client.get("/api/books")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json["count"], 400)
        self.assertEqual(set(response.json["genres"]), set(GENRES))

    def test_search_filter_combination(self):
        response = self.client.post("/api/search", json={
            "genre": "Приключения",
            "max_pages": "200",
            "preference": "Много приключений"
        })
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json["count"], 0)
        for book in response.json["books"]:
            self.assertEqual(book["genre"], "Приключения")
            self.assertLessEqual(book["pages"], 200)
            self.assertIn("Много приключений", book["preferences"])

    def test_each_genre_returns_books(self):
        for genre in GENRES:
            response = self.client.post("/api/search", json={"genre": genre})
            self.assertEqual(response.status_code, 200)
            self.assertGreater(response.json["count"], 0, genre)
            self.assertTrue(all(book["genre"] == genre for book in response.json["books"]))

    def test_page_filter(self):
        response = self.client.post("/api/search", json={"max_pages": "100"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json["count"], 0)
        self.assertTrue(all(book["pages"] <= 100 for book in response.json["books"]))

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")
        self.assertGreaterEqual(response.json["books"], 400)


if __name__ == "__main__":
    unittest.main()
