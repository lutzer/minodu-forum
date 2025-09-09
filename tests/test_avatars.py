import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection, get_db

from src.models.avatar import Avatar

import mimetypes

script_dir = os.path.dirname(os.path.abspath(__file__))

# Create test client
client = TestClient(app)

def create_avatar(file_path: str):
    with open(file_path, "rb") as f:
        response = client.post(
            "/avatars/create",
            files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])}
        )
    return response.json()

class TestAvatarsApi:

    def test_create_avatar(self):

        file_path = os.path.join(script_dir, "files/laura.jpeg")
        with open(file_path, "rb") as f:
            response = client.post(
                "/avatars/create",
                files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"].startswith("image")
        assert os.path.isfile(data['file_path'])

    def test_fail_to_create_avatar_wrong_filetype(self):
        file_path = os.path.join(script_dir, "files/french_sample.mp3")
        with open(file_path, "rb") as f:
            response = client.post(
                "/avatars/create",
                files={"file": (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])}
            )
        assert response.status_code != 200

    def test_list_avatars(self):
        file_path = os.path.join(script_dir, "files/laura.jpeg")
        create_avatar(file_path)
        create_avatar(file_path)

        response = client.get("/avatars")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_avatar(self):
        file_path = os.path.join(script_dir, "files/laura.jpeg")
        avatar = create_avatar(file_path)

        assert os.path.isfile(avatar['file_path'])
    
        response = client.delete(
            f"/avatars/{avatar['id']}"
        )

        assert response.status_code == 200
        assert not os.path.isfile(avatar['file_path'])

    