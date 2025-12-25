# src/tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient

from src.main import app

# Эти записи ДОЛЖНЫ быть заранее загнаны в БД (скриптом перед pytest)
TEST_BOOK_1_TITLE = "CI Book One"
TEST_BOOK_2_TITLE = "CI Book Two"
TEST_BRANCH_1_NAME = "CI Branch One"
TEST_BRANCH_2_NAME = "CI Branch Two"


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
    # DB URL должен быть выставлен CI-скриптом
    assert os.getenv("DATABASE_URL"), "DATABASE_URL is not set (CI should export it before pytest)"

    c = TestClient(app)
    yield c
    c.close()


@pytest.fixture(scope="session")
def book1(client):
    return _require_entity(client, "/books", "title", TEST_BOOK_1_TITLE)


@pytest.fixture(scope="session")
def book2(client):
    return _require_entity(client, "/books", "title", TEST_BOOK_2_TITLE)


@pytest.fixture(scope="session")
def branch1(client):
    return _require_entity(client, "/branches", "name", TEST_BRANCH_1_NAME)


@pytest.fixture(scope="session")
def branch2(client):
    return _require_entity(client, "/branches", "name", TEST_BRANCH_2_NAME)
