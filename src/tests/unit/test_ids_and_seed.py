import main


def test_get_next_book_id_increments():
    main.book_id_seq = 0
    assert main.get_next_book_id() == 1
    assert main.get_next_book_id() == 2


def test_get_next_branch_id_increments():
    main.branch_id_seq = 0
    assert main.get_next_branch_id() == 1
    assert main.get_next_branch_id() == 2


def test_get_next_faculty_id_increments():
    main.faculty_id_seq = 0
    assert main.get_next_faculty_id() == 1
    assert main.get_next_faculty_id() == 2


def test_seed_data_populates_storage():
    assert len(main.branches) >= 2
    assert len(main.books) >= 2
    assert len(main.faculties) >= 2

    assert any(k in main.branch_stock for k in main.branch_stock.keys())
    assert any(k in main.book_faculties for k in main.book_faculties.keys())
