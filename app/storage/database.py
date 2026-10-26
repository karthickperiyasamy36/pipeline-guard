
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""


def create_database_engine(database_url: str) -> Engine:
    """Create a database engine for the supplied database URL."""
    if not database_url or not database_url.strip():
        raise ValueError("Database URL must not be empty.")

    engine_options = {"pool_pre_ping": True}

    # SQLite needs this option for connections used by different threads,
    # such as when an API or dashboard accesses the database.
    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}

    return create_engine(database_url, **engine_options)


def create_tables(engine: Engine) -> None:
    """Create all tables registered with the application's Base."""
    # Import models here so their tables are registered before create_all().
    from app.storage import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session_factory(engine: Engine):
    """Return a factory that creates database sessions."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
