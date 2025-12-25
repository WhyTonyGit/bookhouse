def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_books(client):
    r = client.get("/books")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert {"id", "title", "author", "year"} <= set(data[0].keys())


def test_get_book_ok(client):
    r = client.get("/books/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_book_404(client):
    r = client.get("/books/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_create_book(client):
    payload = {"title": "Clean Code", "author": "Robert C. Martin", "year": 2008}
    r = client.post("/books", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["id"] >= 1
    assert created["title"] == payload["title"]

    # проверяем что реально появилась
    r2 = client.get(f"/books/{created['id']}")
    assert r2.status_code == 200
    assert r2.json()["author"] == payload["author"]


def test_update_book_ok(client):
    payload = {"title": "Новая", "author": "Автор", "year": 2024}
    r = client.put("/books/1", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["id"] == 1
    assert updated["title"] == "Новая"


def test_update_book_404(client):
    payload = {"title": "X", "author": "Y", "year": 2024}
    r = client.put("/books/9999", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_list_branches(client):
    r = client.get("/branches")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2
    assert {"id", "name", "address"} <= set(data[0].keys())


def test_get_branch_ok(client):
    r = client.get("/branches/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_branch_404(client):
    r = client.get("/branches/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_create_branch(client):
    payload = {"name": "Новый филиал", "address": "ул. Тестовая, 10"}
    r = client.post("/branches", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["id"] >= 1
    assert created["name"] == payload["name"]


def test_update_branch_ok(client):
    payload = {"name": "Переименован", "address": "где-то"}
    r = client.put("/branches/1", json=payload)
    assert r.status_code == 200
    assert r.json()["name"] == "Переименован"


def test_update_branch_404(client):
    payload = {"name": "X", "address": "Y"}
    r = client.put("/branches/9999", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_list_faculties(client):
    r = client.get("/faculties")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2
    assert {"id", "name"} <= set(data[0].keys())
