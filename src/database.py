import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import Column, Integer, String
from contextlib import contextmanager
from typing import Generator
import logging

from .config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseConnection:
    _instance = None
    
    @classmethod
    def get_instance(cls, database_url: str):
        if cls._instance is None:
            cls._instance = cls(database_url)
        return cls._instance
    
    def __init__(self, database_url : str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables defined in Base metadata."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables defined in Base metadata."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles session lifecycle and rollback on errors.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """
        Get a session directly (caller responsible for closing).
        Use get_session() context manager instead when possible.
        """
        return self.SessionLocal()
    
    def close(self):
        """Close the engine and all connections."""
        self.engine.dispose()

def get_db_connection():
    return DatabaseConnection.get_instance(Config().database_url)

# Dependency function for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes.
    This function will be used with Depends() to inject database sessions.
    """
    
    session = get_db_connection().get_session_direct()
    try:
        yield session
    finally:
        session.close()

def get_db_transaction() -> Generator[Session, None, None]:
    """
    Database dependency with automatic transaction management.
    Use this for operations that need transaction safety.
    """
    with get_db_connection().get_session() as session:
        yield session