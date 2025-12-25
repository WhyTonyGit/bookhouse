import os
import uuid

import pytest
from fastapi.testclient import TestClient

from src.main import app


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def client():
    # Жёстко валимся, если забыли переменную окружения
    assert os.getenv("DATABASE_URL"), "DATABASE_URL is not set (CI should export it before pytest)"

    # Важно: context manager => гарантированно отрабатывает startup (create_all + seed если он есть)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def book1(client):
    payload = {"title": _unique("book-one"), "author": "Test Author", "year": 2001}
    r = client.post("/books", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def book2(client):
    payload = {"title": _unique("book-two"), "author": "Test Author", "year": 2002}
    r = client.post("/books", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def branch1(client):
    payload = {"name": _unique("branch-one"), "address": "Test street, 1"}
    r = client.post("/branches", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def branch2(client):
    payload = {"name": _unique("branch-two"), "address": "Test street, 2"}
    r = client.post("/branches", json=payload)
    assert r.status_code == 201, r.text
    return r.json()
