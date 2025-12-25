def _find_by(items, key, value):
    for x in items:
        if x.get(key) == value:
            return x
    return None


def test_copies_in_branch(client):
    branches = client.get("/branches").json()
    books = client.get("/books").json()

    main = _find_by(branches, "name", "Главный филиал")
    book1 = _find_by(books, "title", "Алгоритмы: построение и анализ")

    r = client.get(f"/branches/{main['id']}/books/{book1['id']}/copies")
    assert r.status_code == 200
    assert r.json()["copies"] == 5


def test_book_faculties_and_add(client):
    branches = client.get("/branches").json()
    books = client.get("/books").json()
    faculties = client.get("/faculties").json()

    it_branch = _find_by(branches, "name", "ИТ-филиал")
    book1 = _find_by(books, "title", "Алгоритмы: построение и анализ")

    # до добавления
    r1 = client.get(f"/branches/{it_branch['id']}/books/{book1['id']}/faculties")
    assert r1.status_code == 200
    before = r1.json()["faculty_count"]

    # добавим матфак в ИТ-филиал (если вдруг уже есть — ок)
    math = _find_by(faculties, "name", "Математический факультет")
    r2 = client.post(f"/branches/{it_branch['id']}/books/{book1['id']}/faculties/{math['id']}")
    assert r2.status_code == 200
    after = r2.json()["faculty_count"]

    assert after >= before
