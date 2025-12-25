from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.db import engine, get_db
from src.models import Base, Book as BookORM, Branch as BranchORM, Faculty as FacultyORM
from src.models import BranchStock as BranchStockORM, BookFaculty as BookFacultyORM


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
# INIT DB + SEED
# ==========================

def seed_data(db: Session) -> None:
    # если уже есть книги — значит сидили
    books_cnt = db.scalar(select(func.count(BookORM.id)))
    if books_cnt and books_cnt > 0:
        return

    main_branch = BranchORM(name="Главный филиал", address="ул. Академическая, 1")
    it_branch = BranchORM(name="ИТ-филиал", address="пр-т Программистов, 42")
    db.add_all([main_branch, it_branch])
    db.flush()

    book1 = BookORM(title="Алгоритмы: построение и анализ", author="Кормен и др.", year=2009)
    book2 = BookORM(title="Введение в машинное обучение", author="А. Н. Авторов", year=2020)
    db.add_all([book1, book2])
    db.flush()

    fac_it = FacultyORM(name="Факультет информационных технологий")
    fac_math = FacultyORM(name="Математический факультет")
    db.add_all([fac_it, fac_math])
    db.flush()

    # Наличие
    db.add_all([
        BranchStockORM(branch_id=main_branch.id, book_id=book1.id, copies=5),
        BranchStockORM(branch_id=main_branch.id, book_id=book2.id, copies=2),
        BranchStockORM(branch_id=it_branch.id, book_id=book1.id, copies=3),
    ])

    # Использование факультетами
    db.add_all([
        BookFacultyORM(branch_id=main_branch.id, book_id=book1.id, faculty_id=fac_it.id),
        BookFacultyORM(branch_id=main_branch.id, book_id=book1.id, faculty_id=fac_math.id),
        BookFacultyORM(branch_id=it_branch.id, book_id=book1.id, faculty_id=fac_it.id),
        BookFacultyORM(branch_id=main_branch.id, book_id=book2.id, faculty_id=fac_math.id),
    ])

    db.commit()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # сидим через обычную сессию
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

    exists = db.get(BookFacultyORM, {"branch_id": branch_id, "book_id": book_id, "faculty_id": faculty_id})
    if not exists:
        db.add(BookFacultyORM(branch_id=branch_id, book_id=book_id, faculty_id=faculty_id))
        db.commit()

    return get_book_faculties(branch_id, book_id, db)
