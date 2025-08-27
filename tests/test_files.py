import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection, get_db

from .test_authors import create_author
from .test_posts import create_post

from src.models.file import File

import mimetypes

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

def upload_file(post_id: int, file_path: str, auth_token: str):
    with open(file_path, "rb") as f:
        response = client.post(
            "/files/upload",
            files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])},
            data={"post_id": post_id},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    return response.json()

class TestFilesApi:

    def test_upload_image_file(self):
        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")

        file_path = os.path.join(script_dir, "files/laura.jpeg")
        with open(file_path, "rb") as f:
            response = client.post(
                "/files/upload",
                files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])},
                data={"post_id": post["id"]},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"].startswith("image")
    
    def test_upload_audio_file(self):
        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")

        file_path = os.path.join(script_dir, "files/french_sample.mp3")
        with open(file_path, "rb") as f:
            response = client.post(
                "/files/upload",
                files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])},
                data={"post_id": post["id"]},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"].startswith("audio")

    def test_upload_wrong_file(self):
        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")

        file_path = os.path.join(script_dir, "files/laura.jpeg.zip")
        with open(file_path, "rb") as f:
            response = client.post(
                "/files/upload",
                files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])},
                data={"post_id": post["id"]},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        assert response.status_code == 500


    def test_attach_file(self):
        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")

        file_path = os.path.join(script_dir, "files/laura.jpeg")
        file = upload_file(post['id'],file_path, auth_token)

        response = client.get(app.root_path + "/posts/")        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data[0]["files"][0]['filename'] == file["filename"]
    