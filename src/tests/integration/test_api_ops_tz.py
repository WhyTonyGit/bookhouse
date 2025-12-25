# src/tests/integration/test_ops_seeded.py
import pytest


# ----- helpers -----
def _find_by(items, field, value):
    for x in items:
        if x.get(field) == value:
            return x
    return None


def _require_seed_entity(client, endpoint, field, value):
    r = client.get(endpoint)
    assert r.status_code == 200, r.text
    item = _find_by(r.json(), field, value)
    assert item is not None, f"Seed data missing: {endpoint} with {field}='{value}'. DB must be fresh or seed must run."
    return item


@pytest.fixture(scope="session")
def seeded_ids(client):
    """
    Берём id-шники по данным, которые сидятся в seed_data().
    Если этих записей нет — тест падает с понятным сообщением (а не рандомом).
    """
    # branches
    main_branch = _require_seed_entity(client, "/branches", "name", "Главный филиал")
    it_branch = _require_seed_entity(client, "/branches", "name", "ИТ-филиал")

    # books
    books = client.get("/books").json()
    book1 = _find_by(books, "title", "Алгоритмы: построение и анализ")
    book2 = _find_by(books, "title", "Введение в машинное обучение")
    assert book1 is not None, "Seed data missing book1 title"
    assert book2 is not None, "Seed data missing book2 title"

    # faculties (тут только GET, поэтому тоже берём из сидов)
    facs = client.get("/faculties").json()
    fac_it = _find_by(facs, "name", "Факультет информационных технологий")
    fac_math = _find_by(facs, "name", "Математический факультет")
    assert fac_it is not None, "Seed data missing faculty IT"
    assert fac_math is not None, "Seed data missing faculty Math"

    return {
        "main_branch_id": main_branch["id"],
        "it_branch_id": it_branch["id"],
        "book1_id": book1["id"],
        "book2_id": book2["id"],
        "fac_it_id": fac_it["id"],
        "fac_math_id": fac_math["id"],
    }


# ----- tests -----
def test_get_copies_in_branch_existing_pair(client, seeded_ids):
    # В seed_data(): main_branch-book1 copies=5
    r = client.get(f"/branches/{seeded_ids['main_branch_id']}/books/{seeded_ids['book1_id']}/copies")
    assert r.status_code == 200
    body = r.json()
    assert body["branch_id"] == seeded_ids["main_branch_id"]
    assert body["book_id"] == seeded_ids["book1_id"]
    assert body["copies"] == 5


def test_get_copies_in_branch_missing_pair_returns_zero(client, seeded_ids):
    # В seed_data(): it_branch-book2 НЕ добавлялся => 0
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
    # В seed_data(): main_branch-book1 => 2 факультета
    r = client.get(f"/branches/{seeded_ids['main_branch_id']}/books/{seeded_ids['book1_id']}/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 2
    assert isinstance(body["faculties"], list)
    assert {f["name"] for f in body["faculties"]}  # не пусто


def test_get_book_faculties_for_missing_relation_returns_empty(client, seeded_ids):
    # В seed_data(): it_branch-book2 => связей нет
    r = client.get(f"/branches/{seeded_ids['it_branch_id']}/books/{seeded_ids['book2_id']}/faculties")
    assert r.status_code == 200
    body = r.json()
    assert body["faculty_count"] == 0
    assert body["faculties"] == []


def test_add_book_faculty_ok(client, seeded_ids):
    # В seed_data(): it_branch-book1 имеет fac_it.
    # Добавим fac_math => станет 2
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
