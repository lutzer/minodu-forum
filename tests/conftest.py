import pytest
import os

from src.database import get_db_transaction, get_db_connection
from src.models.file import File
from src.models.avatar import Avatar

@pytest.fixture(autouse=True)
def set_test_database_url(monkeypatch):
    # Set a test-specific database URL and create tables
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_database.db")
    monkeypatch.setenv("UPLOAD_DIR", "tests/tmp")
    monkeypatch.setenv("AVATAR_UPLOAD_DIR", "tests/tmp")
    monkeypatch.setenv("AI_SERVICE_URL", "http://0.0.0.0:3001/services")
    get_db_connection().create_tables()
    
    yield

    # Delete all files before dropping database table
    db = get_db_connection().get_session_direct()
    files = db.query(File).all()
    for file in files:
        os.remove(file.file_path)

    # Delete all avatars
    db = get_db_connection().get_session_direct()
    avatars = db.query(Avatar).all()
    for avatar in avatars:
        os.remove(avatar.file_path)

    get_db_connection().drop_tables()

    