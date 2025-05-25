# app/core/database.py

import databases  # For async raw SQL, if used in services
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session  # Import Session for type hinting

from app.core.config import settings

# SQLAlchemy setup for ORM
# metadata is a container for schema information.
metadata = MetaData()

# Base is the base class for your SQLAlchemy ORM models (e.g., User, Todo).
Base = declarative_base(metadata=metadata)

# The database engine is the entry point to your database.
# For SQLite, connect_args={"check_same_thread": False} is needed because
# FastAPI, by default, might interact with the DB from different threads
# than where it was created (for async path operations calling sync DB code).
engine = create_engine(
    settings.DATABASE_URL,
    # connect_args should be conditional on the database type
    # For PostgreSQL or MySQL, this connect_args is not needed.
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    ),
)

# SessionLocal is a factory for creating new SQLAlchemy Session objects.
# Each session is a "conversation" with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# `databases` library setup (for async raw SQL queries)
# This 'database' object can be used for performing asynchronous database operations
# directly, often for queries where the ORM might be too cumbersome or for raw speed.
# Example usage in an async service: await database.fetch_all(query)
# If your services are primarily using SQLAlchemy ORM with the session from get_db,
# you might not use this 'database' object as frequently in those specific services.
database = databases.Database(settings.DATABASE_URL)


# FastAPI Dependency to get a DB session
def get_db() -> (
    Session
):  # Changed to yield Session for type hinting, though it yields a generator
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    It ensures the session is opened at the start of a request
    and closed at the end, even if errors occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Functions to connect/disconnect the `databases` instance if used globally
# (e.g., in FastAPI startup/shutdown events)
# async def connect_db_async():
#     await database.connect()

# async def disconnect_db_async():
#     await database.disconnect()
