import os
import pytest
from fastapi.testclient import TestClient

from src.main import app


# --- constants required by tests (must exist in DB before pytest) ---
CI_BOOK_1_TITLE = "CI Book One"
CI_BOOK_2_TITLE = "CI Book Two"
CI_BRANCH_1_NAME = "CI Branch One"
CI_BRANCH_2_NAME = "CI Branch Two"


# ----- helpers -----
def _find_by(items, field, value):
    for x in items:
        if x.get(field) == value:
            return x
    return None


def _require_entity(client: TestClient, endpoint: str, field: str, value: str):
    r = client.get(endpoint)
    assert r.status_code == 200, r.text
    item = _find_by(r.json(), field, value)
    assert item is not None, (
        f"Seed data missing: {endpoint} with {field}='{value}'. "
        f"Pre-seed DB before pytest."
    )
    return item


@pytest.fixture(scope="session")
def client():
    # Жёстко валимся, если забыли переменную окружения
    assert os.getenv("DATABASE_URL"), "DATABASE_URL is not set (CI should export it before pytest)"

    # важно: startup должен отработать один раз на всю сессию
    # (создание схемы/сидирование делаем ДО pytest в CI-скрипте, а тут просто используем)
    with TestClient(app) as c:
        yield c


# --- entities used by “created” tests (but created заранее через seed) ---
@pytest.fixture()
def book1(client):
    return _require_entity(client, "/books", "title", CI_BOOK_1_TITLE)


@pytest.fixture()
def book2(client):
    return _require_entity(client, "/books", "title", CI_BOOK_2_TITLE)


@pytest.fixture()
def branch1(client):
    return _require_entity(client, "/branches", "name", CI_BRANCH_1_NAME)


@pytest.fixture()
def branch2(client):
    return _require_entity(client, "/branches", "name", CI_BRANCH_2_NAME)


@pytest.fixture()
def seeded_ids(client):
    """
    Берём id-шники по данным, которые сидятся в seed_data().
    Если этих записей нет — тест падает с понятным сообщением.
    """
    # branches
    main_branch = _require_entity(client, "/branches", "name", "Главный филиал")
    it_branch = _require_entity(client, "/branches", "name", "ИТ-филиал")

    # books
    books = client.get("/books").json()
    book1_seed = _find_by(books, "title", "Алгоритмы: построение и анализ")
    book2_seed = _find_by(books, "title", "Введение в машинное обучение")
    assert book1_seed is not None, "Seed data missing book1 title"
    assert book2_seed is not None, "Seed data missing book2 title"

    # faculties
    facs = client.get("/faculties").json()
    fac_it = _find_by(facs, "name", "Факультет информационных технологий")
    fac_math = _find_by(facs, "name", "Математический факультет")
    assert fac_it is not None, "Seed data missing faculty IT"
    assert fac_math is not None, "Seed data missing faculty Math"

    return {
        "main_branch_id": main_branch["id"],
        "it_branch_id": it_branch["id"],
        "book1_id": book1_seed["id"],
        "book2_id": book2_seed["id"],
        "fac_it_id": fac_it["id"],
        "fac_math_id": fac_math["id"],
    }
