from typing import Dict, List, Tuple, Set
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="BookHouse (demo без БД)",
    description="Простое учебное приложение библиотеки с хранением данных в памяти.",
    version="0.1.0",
)

# ==========================
# МОДЕЛИ ДАННЫХ (Pydantic)
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
# "БД" В ПАМЯТИ
# ==========================

books: Dict[int, Book] = {}
branches: Dict[int, Branch] = {}
faculties: Dict[int, Faculty] = {}

# ключ: (branch_id, book_id) -> количество экземпляров
branch_stock: Dict[Tuple[int, int], int] = {}

# ключ: (branch_id, book_id) -> множество faculty_id
book_faculties: Dict[Tuple[int, int], Set[int]] = {}

# простые автоинкременты ID
book_id_seq: int = 0
branch_id_seq: int = 0
faculty_id_seq: int = 0


def get_next_book_id() -> int:
    global book_id_seq
    book_id_seq += 1
    return book_id_seq


def get_next_branch_id() -> int:
    global branch_id_seq
    branch_id_seq += 1
    return branch_id_seq


def get_next_faculty_id() -> int:
    global faculty_id_seq
    faculty_id_seq += 1
    return faculty_id_seq


# ==========================
# НАЧАЛЬНЫЕ ДЕМO-ДАННЫЕ
# ==========================


def seed_data() -> None:
    # Филиалы
    main_branch = Branch(
        id=get_next_branch_id(), name="Главный филиал", address="ул. Академическая, 1"
    )
    it_branch = Branch(
        id=get_next_branch_id(), name="ИТ-филиал", address="пр-т Программистов, 42"
    )
    branches[main_branch.id] = main_branch
    branches[it_branch.id] = it_branch

    # Книги
    book1 = Book(
        id=get_next_book_id(),
        title="Алгоритмы: построение и анализ",
        author="Кормен и др.",
        year=2009,
    )
    book2 = Book(
        id=get_next_book_id(),
        title="Введение в машинное обучение",
        author="А. Н. Авторов",
        year=2020,
    )
    books[book1.id] = book1
    books[book2.id] = book2

    # Факультеты
    fac_it = Faculty(id=get_next_faculty_id(), name="Факультет информационных технологий")
    fac_math = Faculty(id=get_next_faculty_id(), name="Математический факультет")
    faculties[fac_it.id] = fac_it
    faculties[fac_math.id] = fac_math

    # Наличие книг по филиалам
    branch_stock[(main_branch.id, book1.id)] = 5
    branch_stock[(main_branch.id, book2.id)] = 2
    branch_stock[(it_branch.id, book1.id)] = 3

    # Использование книг факультетами в конкретных филиалах
    # Книга 1 используется ИТ и матфаком в главном филиале
    book_faculties[(main_branch.id, book1.id)] = {fac_it.id, fac_math.id}
    # Книга 1 только ИТ-факультетом в ИТ-филиале
    book_faculties[(it_branch.id, book1.id)] = {fac_it.id}
    # Книга 2 только матфаком в главном филиале
    book_faculties[(main_branch.id, book2.id)] = {fac_math.id}


seed_data()

# ==========================
# HEALTH-CHECK
# ==========================


@app.get("/health")
def health_check():
    """
    Простая ручка для проверки, что приложение живо.
    """
    return {"status": "ok"}


# ==========================
# КНИГИ
# ==========================


@app.get("/books", response_model=List[Book])
def list_books():
    return list(books.values())


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@app.post("/books", response_model=Book, status_code=201)
def create_book(data: BookBase):
    new_id = get_next_book_id()
    book = Book(id=new_id, **data.dict())
    books[new_id] = book
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, data: BookBase):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    updated = Book(id=book_id, **data.dict())
    books[book_id] = updated
    return updated


# ==========================
# ФИЛИАЛЫ
# ==========================


@app.get("/branches", response_model=List[Branch])
def list_branches():
    return list(branches.values())


@app.get("/branches/{branch_id}", response_model=Branch)
def get_branch(branch_id: int):
    branch = branches.get(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    return branch


@app.post("/branches", response_model=Branch, status_code=201)
def create_branch(data: BranchBase):
    new_id = get_next_branch_id()
    branch = Branch(id=new_id, **data.dict())
    branches[new_id] = branch
    return branch


@app.put("/branches/{branch_id}", response_model=Branch)
def update_branch(branch_id: int, data: BranchBase):
    if branch_id not in branches:
        raise HTTPException(status_code=404, detail="Филиал не найден")

    updated = Branch(id=branch_id, **data.dict())
    branches[branch_id] = updated
    return updated


# ==========================
# ФАКУЛЬТЕТЫ
# ==========================


@app.get("/faculties", response_model=List[Faculty])
def list_faculties():
    return list(faculties.values())


# ==========================
# ОПЕРАЦИИ ПО ТЗ
# ==========================


@app.get(
    "/branches/{branch_id}/books/{book_id}/copies",
    response_model=BranchBookInfo,
)
def get_copies_in_branch(branch_id: int, book_id: int):
    """
    1) Для указанного филиала подсчитывает количество экземпляров
       указанной книги, находящихся в нём.
    """
    if branch_id not in branches:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    copies = branch_stock.get((branch_id, book_id), 0)
    return BranchBookInfo(branch_id=branch_id, book_id=book_id, copies=copies)


@app.get(
    "/branches/{branch_id}/books/{book_id}/faculties",
    response_model=BookFacultiesResponse,
)
def get_book_faculties(branch_id: int, book_id: int):
    """
    2) Для указанной книги подсчитывает количество факультетов,
       на которых она используется в данном филиале, и выводит названия этих факультетов.
    """
    if branch_id not in branches:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    faculty_ids = book_faculties.get((branch_id, book_id), set())
    faculty_list: List[Faculty] = []

    for fid in faculty_ids:
        fac = faculties.get(fid)
        if fac:
            faculty_list.append(fac)

    return BookFacultiesResponse(
        branch_id=branch_id,
        book_id=book_id,
        faculty_count=len(faculty_list),
        faculties=faculty_list,
    )


@app.post(
    "/branches/{branch_id}/books/{book_id}/faculties/{faculty_id}",
    response_model=BookFacultiesResponse,
)
def add_book_faculty(branch_id: int, book_id: int, faculty_id: int):
    """
    Доп. ручка: привязать книгу к факультету в филиале (для тестов).
    """
    if branch_id not in branches:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if faculty_id not in faculties:
        raise HTTPException(status_code=404, detail="Факультет не найден")

    key = (branch_id, book_id)
    if key not in book_faculties:
        book_faculties[key] = set()
    book_faculties[key].add(faculty_id)

    faculty_list = [faculties[fid] for fid in book_faculties[key]]
    return BookFacultiesResponse(
        branch_id=branch_id,
        book_id=book_id,
        faculty_count=len(faculty_list),
        faculties=faculty_list,
    )


# ==========================
# ЗАПУСК ЧЕРЕЗ `python main.py`
# ==========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
