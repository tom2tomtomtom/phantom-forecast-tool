"""
Database connection and session management for the Phantom Forecast Tool.

Copied from congressional-trading-system with minimal adaptations.
Uses SUPABASE_DATABASE_URL for PostgreSQL connection.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Get database URL from environment (Railway uses DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DATABASE_URL", "sqlite:///./phantom_forecast.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Create database engine
# Use different configurations for SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=DEBUG,
    )

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL (Supabase) or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300,
        echo=DEBUG,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI dependencies.

    Example:
        with get_db_context() as db:
            items = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def close_db() -> None:
    """Close database connections."""
    engine.dispose()
