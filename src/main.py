# src/main.py
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db import engine, get_db
from src.models import (
    Base,
    Book as BookORM,
    Branch as BranchORM,
    Faculty as FacultyORM,
    BranchStock as BranchStockORM,
    BookFaculty as BookFacultyORM,
)

app = FastAPI(
    title="BookHouse (PostgreSQL)",
    description="Учебное приложение библиотеки с PostgreSQL.",
    version="0.2.0",
)

# ==========================
# SCHEMAS (Pydantic)
# ==========================


class BookBase(BaseModel):
    title: str
    author: str
    year: int | None = None


class Book(BookBase):
    id: int


class BranchBase(BaseModel):
    name: str
    address: str | None = None


class Branch(BranchBase):
    id: int


class Faculty(BaseModel):
    id: int
    name: str


class BranchBookInfo(BaseModel):
    branch_id: int
    book_id: int
    copies: int


class BookFacultiesResponse(BaseModel):
    branch_id: int
    book_id: int
    faculty_count: int
    faculties: List[Faculty]


# ==========================
# INIT DB + SEED (idempotent)
# ==========================


def _get_branch_by_name(db: Session, name: str) -> BranchORM | None:
    return db.scalar(select(BranchORM).where(BranchORM.name == name))


def _get_book_by_title(db: Session, title: str) -> BookORM | None:
    return db.scalar(select(BookORM).where(BookORM.title == title))


def _get_faculty_by_name(db: Session, name: str) -> FacultyORM | None:
    return db.scalar(select(FacultyORM).where(FacultyORM.name == name))


def _ensure_branch(db: Session, *, name: str, address: str | None) -> BranchORM:
    branch = _get_branch_by_name(db, name)
    if branch is None:
        branch = BranchORM(name=name, address=address)
        db.add(branch)
        db.flush()
    else:
        # обновляем адрес, если вдруг пустой/устарел
        if address is not None and branch.address != address:
            branch.address = address
            db.flush()
    return branch


def _ensure_book(db: Session, *, title: str, author: str, year: int | None) -> BookORM:
    book = _get_book_by_title(db, title)
    if book is None:
        book = BookORM(title=title, author=author, year=year)
        db.add(book)
        db.flush()
    else:
        # делаем данные стабильными для тестов
        changed = False
        if book.author != author:
            book.author = author
            changed = True
        if book.year != year:
            book.year = year
            changed = True
        if changed:
            db.flush()
    return book


def _ensure_faculty(db: Session, *, name: str) -> FacultyORM:
    fac = _get_faculty_by_name(db, name)
    if fac is None:
        fac = FacultyORM(name=name)
        db.add(fac)
        db.flush()
    return fac


def _ensure_stock(db: Session, *, branch_id: int, book_id: int, copies: int) -> None:
    row = db.scalar(
        select(BranchStockORM).where(
            BranchStockORM.branch_id == branch_id,
            BranchStockORM.book_id == book_id,
        )
    )
    if row is None:
        db.add(BranchStockORM(branch_id=branch_id, book_id=book_id, copies=copies))
    else:
        if row.copies != copies:
            row.copies = copies


def _ensure_book_faculty(db: Session, *, branch_id: int, book_id: int, faculty_id: int) -> None:
    row = db.scalar(
        select(BookFacultyORM).where(
            BookFacultyORM.branch_id == branch_id,
            BookFacultyORM.book_id == book_id,
            BookFacultyORM.faculty_id == faculty_id,
        )
    )
    if row is None:
        db.add(BookFacultyORM(branch_id=branch_id, book_id=book_id, faculty_id=faculty_id))


def seed_data(db: Session) -> None:
    """
    Сидирование должно быть:
    - детерминированным (тесты ожидают конкретные записи)
    - идемпотентным (можно вызывать много раз без дублей)
    """

    # просто проверка, что таблицы вообще доступны
    db.scalar(select(func.count(BookORM.id)))

    # --- branches (seed + CI required) ---
    main_branch = _ensure_branch(db, name="Главный филиал", address="ул. Академическая, 1")
    it_branch = _ensure_branch(db, name="ИТ-филиал", address="пр-т Программистов, 42")

    ci_branch_one = _ensure_branch(db, name="CI Branch One", address="Test street, 1")
    ci_branch_two = _ensure_branch(db, name="CI Branch Two", address="Test street, 2")

    # --- books (seed + CI required) ---
    book_seed_1 = _ensure_book(
        db,
        title="Алгоритмы: построение и анализ",
        author="Кормен и др.",
        year=2009,
    )
    book_seed_2 = _ensure_book(
        db,
        title="Введение в машинное обучение",
        author="А. Н. Авторов",
        year=2020,
    )

    ci_book_one = _ensure_book(db, title="CI Book One", author="Test Author", year=2001)
    ci_book_two = _ensure_book(db, title="CI Book Two", author="Test Author", year=2002)

    # --- faculties ---
    fac_it = _ensure_faculty(db, name="Факультет информационных технологий")
    fac_math = _ensure_faculty(db, name="Математический факультет")

    # --- stock (наличие) ---
    _ensure_stock(db, branch_id=main_branch.id, book_id=book_seed_1.id, copies=5)
    _ensure_stock(db, branch_id=main_branch.id, book_id=book_seed_2.id, copies=2)
    _ensure_stock(db, branch_id=it_branch.id, book_id=book_seed_1.id, copies=3)

    # --- book<->faculty usage in branches ---
    _ensure_book_faculty(db, branch_id=main_branch.id, book_id=book_seed_1.id, faculty_id=fac_it.id)
    _ensure_book_faculty(db, branch_id=main_branch.id, book_id=book_seed_1.id, faculty_id=fac_math.id)
    _ensure_book_faculty(db, branch_id=it_branch.id, book_id=book_seed_1.id, faculty_id=fac_it.id)
    _ensure_book_faculty(db, branch_id=main_branch.id, book_id=book_seed_2.id, faculty_id=fac_math.id)

    # CI entities deliberately have NO special relations/stocks (тесты это не требуют)

    db.commit()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from src.db import SessionLocal

    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


# ==========================
# HEALTH
# ==========================


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ==========================
# BOOKS
# ==========================


@app.get("/books", response_model=List[Book])
def list_books(db: Session = Depends(get_db)):
    rows = db.scalars(select(BookORM).order_by(BookORM.id)).all()
    return [Book(id=r.id, title=r.title, author=r.author, year=r.year) for r in rows]


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(BookORM, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return Book(id=book.id, title=book.title, author=book.author, year=book.year)


@app.post("/books", response_model=Book, status_code=201)
def create_book(data: BookBase, db: Session = Depends(get_db)):
    book = BookORM(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return Book(id=book.id, title=book.title, author=book.author, year=book.year)


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, data: BookBase, db: Session = Depends(get_db)):
    book = db.get(BookORM, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    payload = data.model_dump()
    book.title = payload["title"]
    book.author = payload["author"]
    book.year = payload["year"]
    db.commit()
    db.refresh(book)

    return Book(id=book.id, title=book.title, author=book.author, year=book.year)


# ==========================
# BRANCHES
# ==========================


@app.get("/branches", response_model=List[Branch])
def list_branches(db: Session = Depends(get_db)):
    rows = db.scalars(select(BranchORM).order_by(BranchORM.id)).all()
    return [Branch(id=r.id, name=r.name, address=r.address) for r in rows]


@app.get("/branches/{branch_id}", response_model=Branch)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.get(BranchORM, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    return Branch(id=branch.id, name=branch.name, address=branch.address)


@app.post("/branches", response_model=Branch, status_code=201)
def create_branch(data: BranchBase, db: Session = Depends(get_db)):
    branch = BranchORM(**data.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return Branch(id=branch.id, name=branch.name, address=branch.address)


@app.put("/branches/{branch_id}", response_model=Branch)
def update_branch(branch_id: int, data: BranchBase, db: Session = Depends(get_db)):
    branch = db.get(BranchORM, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")

    payload = data.model_dump()
    branch.name = payload["name"]
    branch.address = payload["address"]
    db.commit()
    db.refresh(branch)
    return Branch(id=branch.id, name=branch.name, address=branch.address)


# ==========================
# FACULTIES
# ==========================


@app.get("/faculties", response_model=List[Faculty])
def list_faculties(db: Session = Depends(get_db)):
    rows = db.scalars(select(FacultyORM).order_by(FacultyORM.id)).all()
    return [Faculty(id=r.id, name=r.name) for r in rows]


# ==========================
# OPS (ТЗ)
# ==========================


@app.get("/branches/{branch_id}/books/{book_id}/copies", response_model=BranchBookInfo)
def get_copies_in_branch(branch_id: int, book_id: int, db: Session = Depends(get_db)):
    if not db.get(BranchORM, branch_id):
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if not db.get(BookORM, book_id):
        raise HTTPException(status_code=404, detail="Книга не найдена")

    copies = db.scalar(
        select(BranchStockORM.copies).where(
            BranchStockORM.branch_id == branch_id,
            BranchStockORM.book_id == book_id,
        )
    )
    return BranchBookInfo(branch_id=branch_id, book_id=book_id, copies=int(copies or 0))


@app.get("/branches/{branch_id}/books/{book_id}/faculties", response_model=BookFacultiesResponse)
def get_book_faculties(branch_id: int, book_id: int, db: Session = Depends(get_db)):
    if not db.get(BranchORM, branch_id):
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if not db.get(BookORM, book_id):
        raise HTTPException(status_code=404, detail="Книга не найдена")

    rows = db.execute(
        select(FacultyORM.id, FacultyORM.name)
        .join(BookFacultyORM, BookFacultyORM.faculty_id == FacultyORM.id)
        .where(
            BookFacultyORM.branch_id == branch_id,
            BookFacultyORM.book_id == book_id,
        )
        .order_by(FacultyORM.id)
    ).all()

    facs = [Faculty(id=r[0], name=r[1]) for r in rows]
    return BookFacultiesResponse(
        branch_id=branch_id,
        book_id=book_id,
        faculty_count=len(facs),
        faculties=facs,
    )


@app.post("/branches/{branch_id}/books/{book_id}/faculties/{faculty_id}", response_model=BookFacultiesResponse)
def add_book_faculty(branch_id: int, book_id: int, faculty_id: int, db: Session = Depends(get_db)):
    if not db.get(BranchORM, branch_id):
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if not db.get(BookORM, book_id):
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if not db.get(FacultyORM, faculty_id):
        raise HTTPException(status_code=404, detail="Факультет не найден")

    exists = db.scalar(
        select(BookFacultyORM).where(
            BookFacultyORM.branch_id == branch_id,
            BookFacultyORM.book_id == book_id,
            BookFacultyORM.faculty_id == faculty_id,
        )
    )
    if not exists:
        db.add(BookFacultyORM(branch_id=branch_id, book_id=book_id, faculty_id=faculty_id))
        db.commit()

    return get_book_faculties(branch_id, book_id, db)
