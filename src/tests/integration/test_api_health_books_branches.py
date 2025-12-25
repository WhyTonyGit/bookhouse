def _find_by(items, key, value):
    for x in items:
        if x.get(key) == value:
            return x
    return None


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_books_list_and_get(client):
    r = client.get("/books")
    assert r.status_code == 200
    books = r.json()
    assert len(books) >= 2

    book1 = _find_by(books, "title", "Алгоритмы: построение и анализ")
    assert book1 is not None

    r2 = client.get(f"/books/{book1['id']}")
    assert r2.status_code == 200
    assert r2.json()["author"] == "Кормен и др."


def test_create_and_update_book(client):
    payload = {"title": "Тестовая книга", "author": "Я", "year": 2024}
    r = client.post("/books", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["id"] > 0

    upd = {"title": "Тестовая книга 2", "author": "Я", "year": 2025}
    r2 = client.put(f"/books/{created['id']}", json=upd)
    assert r2.status_code == 200
    assert r2.json()["title"] == "Тестовая книга 2"


def test_branches_list(client):
    r = client.get("/branches")
    assert r.status_code == 200
    branches = r.json()
    assert len(branches) >= 2
