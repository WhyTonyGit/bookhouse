# src/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.db import Base, get_engine

def _db_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/bookhouse",
    )

@pytest.fixture(scope="session")
def engine():
    return get_engine(_db_url())

@pytest.fixture(scope="session", autouse=True)
def create_test_schema(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client():
    return TestClient(app)
