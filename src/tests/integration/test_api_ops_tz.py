def test_get_copies_in_branch_existing_pair(client):
    r = client.get("/branches/1/books/1/copies")
    assert r.status_code == 200
    body = r.json()
    assert body["branch_id"] == 1
    assert body["book_id"] == 1
    assert body["copies"] == 5


def test_get_copies_in_branch_missing_pair_returns_zero(client):
    r = client.get("/branches/2/books/2/copies")
    assert r.status_code == 200
    assert r.json()["copies"] == 0


def test_get_copies_branch_404(client):
    r = client.get("/branches/999/books/1/copies")
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_get_copies_book_404(client):
    r = client.get("/branches/1/books/999/copies")
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_get_book_faculties_ok(client):
    r = client.get("/branches/1/books/1/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 2
    assert isinstance(body["faculties"], list)
    assert {f["name"] for f in body["faculties"]}  # не пусто


def test_get_book_faculties_for_missing_relation_returns_empty(client):
    r = client.get("/branches/2/books/2/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 0
    assert body["faculties"] == []


def test_add_book_faculty_ok(client):
    r = client.post("/branches/2/books/1/faculties/2")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 2

    r2 = client.get("/branches/2/books/1/faculties")
    assert r2.status_code == 200
    assert r2.json()["faculty_count"] == 2


def test_add_book_faculty_404_branch(client):
    r = client.post("/branches/999/books/1/faculties/1")
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_add_book_faculty_404_book(client):
    r = client.post("/branches/1/books/999/faculties/1")
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_add_book_faculty_404_faculty(client):
    r = client.post("/branches/1/books/1/faculties/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Факультет не найден"
