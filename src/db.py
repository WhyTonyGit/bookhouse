# src/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/bookhouse",
    )

def get_engine(url: str | None = None):
    return create_engine(url or get_database_url(), pool_pre_ping=True)

engine = get_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
