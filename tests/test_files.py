import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection, get_db

from .test_authors import create_author
from .test_posts import create_post

from src.models.file import File

script_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(autouse=True)
def set_test_database_url(monkeypatch):
    # Set a test-specific database URL and create tables
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_database.db")
    get_db_connection().create_tables()
    yield
    #remove tables after tests
    db = get_db_connection().get_session_direct()
    files = db.query(File).all()
    for file in files:
        os.remove(file.file_path)
    get_db_connection().drop_tables()

# Create test client
client = TestClient(app)

class TestFilesApi:
    def test_upload_file(self):
        author = create_author()
        post = create_post(author['id'], "fetch_test")

        file_path = os.path.join(script_dir, "files/laura.jpeg")
        with open(file_path, "rb") as f:
            response = client.post(
                "/files/upload",
                files={"file": (os.path.basename(file_path), f, "image/jpeg")},
                data={"post_id": post["id"]}
            )
        assert response.status_code == 200
        data = response.json()


    