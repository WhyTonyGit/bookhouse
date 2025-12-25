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
    new_payload = {"title": book1["title"] + "-upd", "author": "Upd Author", "year": 2024}
    r = client.put(f"/books/{book1['id']}", json=new_payload)
    assert r.status_code == 200

    upd = r.json()
    assert upd["id"] == book1["id"]
    assert upd["title"] == new_payload["title"]
    assert upd["author"] == new_payload["author"]
    assert upd["year"] == new_payload["year"]


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


# ----- tests for copies/faculties -----
def test_get_copies_in_branch_existing_pair(client, seeded_ids):
    r = client.get(f"/branches/{seeded_ids['main_branch_id']}/books/{seeded_ids['book1_id']}/copies")
    assert r.status_code == 200
    body = r.json()
    assert body["branch_id"] == seeded_ids["main_branch_id"]
    assert body["book_id"] == seeded_ids["book1_id"]
    assert body["copies"] == 5


def test_get_copies_in_branch_missing_pair_returns_zero(client, seeded_ids):
    r = client.get(f"/branches/{seeded_ids['it_branch_id']}/books/{seeded_ids['book2_id']}/copies")
    assert r.status_code == 200
    assert r.json()["copies"] == 0


def test_get_copies_branch_404(client, seeded_ids):
    r = client.get(f"/branches/999999/books/{seeded_ids['book1_id']}/copies")
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_get_copies_book_404(client, seeded_ids):
    r = client.get(f"/branches/{seeded_ids['main_branch_id']}/books/999999/copies")
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_get_book_faculties_ok(client, seeded_ids):
    r = client.get(f"/branches/{seeded_ids['main_branch_id']}/books/{seeded_ids['book1_id']}/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 2
    assert isinstance(body["faculties"], list)
    assert {f["name"] for f in body["faculties"]}  # not empty


def test_get_book_faculties_for_missing_relation_returns_empty(client, seeded_ids):
    r = client.get(f"/branches/{seeded_ids['it_branch_id']}/books/{seeded_ids['book2_id']}/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 0
    assert body["faculties"] == []


def test_add_book_faculty_ok(client, seeded_ids):
    r = client.post(
        f"/branches/{seeded_ids['it_branch_id']}/books/{seeded_ids['book1_id']}/faculties/{seeded_ids['fac_math_id']}"
    )
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 2

    r2 = client.get(f"/branches/{seeded_ids['it_branch_id']}/books/{seeded_ids['book1_id']}/faculties")
    assert r2.status_code == 200
    assert r2.json()["faculty_count"] == 2


def test_add_book_faculty_404_branch(client, seeded_ids):
    r = client.post(f"/branches/999999/books/{seeded_ids['book1_id']}/faculties/{seeded_ids['fac_it_id']}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Филиал не найден"


def test_add_book_faculty_404_book(client, seeded_ids):
    r = client.post(f"/branches/{seeded_ids['main_branch_id']}/books/999999/faculties/{seeded_ids['fac_it_id']}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Книга не найдена"


def test_add_book_faculty_404_faculty(client, seeded_ids):
    r = client.post(f"/branches/{seeded_ids['main_branch_id']}/books/{seeded_ids['book1_id']}/faculties/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Факультет не найден"
