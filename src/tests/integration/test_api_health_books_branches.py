# src/tests/integration/test_api_health_books_branches.py

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_books_contains_created(client, book1, book2):
    r = client.get("/books")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, list)

    ids = {b["id"] for b in data}
    assert book1["id"] in ids
    assert book2["id"] in ids


def test_get_book_by_id(client, book1):
    r = client.get(f"/books/{book1['id']}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == book1["id"]
    assert got["title"] == book1["title"]
    assert got["author"] == book1["author"]
    assert got["year"] == book1["year"]


def test_update_book(client, book1):
    original = {"title": book1["title"], "author": book1["author"], "year": book1["year"]}

    new_payload = {"title": book1["title"] + "-upd", "author": "Upd Author", "year": 2024}
    try:
        r = client.put(f"/books/{book1['id']}", json=new_payload)
        assert r.status_code == 200

        upd = r.json()
        assert upd["id"] == book1["id"]
        assert upd["title"] == new_payload["title"]
        assert upd["author"] == new_payload["author"]
        assert upd["year"] == new_payload["year"]
    finally:
        # Вернём назад, чтобы не ломать другие тесты на сиды/наличие
        r2 = client.put(f"/books/{book1['id']}", json=original)
        assert r2.status_code == 200


def test_list_branches_contains_created(client, branch1, branch2):
    r = client.get("/branches")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, list)

    ids = {b["id"] for b in data}
    assert branch1["id"] in ids
    assert branch2["id"] in ids


def test_get_branch_by_id(client, branch1):
    r = client.get(f"/branches/{branch1['id']}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == branch1["id"]
    assert got["name"] == branch1["name"]
    assert got["address"] == branch1["address"]
