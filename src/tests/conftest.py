import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.main import app, seed_data
from src.models import Base
from src.db import get_db


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/bookhouse",
)

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _truncate_all(db):
    db.execute(text("TRUNCATE TABLE book_faculties, branch_stock, faculties, branches, books RESTART IDENTITY CASCADE;"))
    db.commit()


@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        _truncate_all(db)
        seed_data(db)
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
