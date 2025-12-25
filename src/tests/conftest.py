import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_in_memory_db():

    main.books.clear()
    main.branches.clear()
    main.faculties.clear()
    main.branch_stock.clear()
    main.book_faculties.clear()

    main.book_id_seq = 0
    main.branch_id_seq = 0
    main.faculty_id_seq = 0

    main.seed_data()
    yield


@pytest.fixture()
def client():
    return TestClient(main.app)
