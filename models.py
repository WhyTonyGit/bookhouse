from sqlalchemy import (
    String, Integer, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


class BranchStock(Base):
    __tablename__ = "branch_stock"
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    copies: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("branch_id", "book_id", name="uq_branch_book_stock"),
    )


class BookFaculty(Base):
    __tablename__ = "book_faculties"
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id", ondelete="CASCADE"), primary_key=True)
