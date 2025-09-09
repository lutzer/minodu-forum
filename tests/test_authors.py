import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection
from tests.test_avatars import create_avatar

script_dir = os.path.dirname(os.path.abspath(__file__))

# Create test client
client = TestClient(app)

def create_author(name: str = "test"):
    author_data = {
        "name": name,
        "avatar": None
    }
    response = client.post(app.root_path + "/authors/create", json=author_data)
    return response.json()["token"]

class TestAuthorsApi:

    def test_create_author(self):
        author_data = {
            "name": "Author1",
            "avatar": None
        }
        response = client.post(app.root_path + "/authors/create", json=author_data)        
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data["token"]) > 0
        assert response_data["id"] >= 0

    def test_fetch_authors(self):
        author_data = {
            "name": "test",
            "avatar": None
        }
        response1 = client.post(app.root_path + "/authors/create", json=author_data)

        response2 = client.get(app.root_path + "/authors/")
        response2_data = response2.json()
        assert response2_data[0]["id"] == response1.json()["id"]

    def test_edit_author_name(self):
        old_data = {
            "name": "old_name"
        }

        response = client.post(app.root_path + "/authors/create", json=old_data)
        token = response.json()['token']
        author_id = response.json()['id']

        new_data = {
            "name": "new_name"
        }

        response = client.put(
            app.root_path + f"/authors/{author_id}", 
            json=new_data,
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()['name'] == new_data['name']

    def test_create_author_with_avatar(self):
        file_path = os.path.join(script_dir, "files/laura.jpeg")
        avatar = create_avatar(file_path)

        author_data = {
            "name": "Author1",
            "avatar": avatar["id"]
        }
        response = client.post(app.root_path + "/authors/create", json=author_data)        
        assert response.status_code == 200
        author_id = response.json()["id"]

        response = client.get(app.root_path + f"/authors/{author_id}")
        assert response.status_code == 200
        assert response.json()["avatar"] != None
        

    def test_edit_author_avatar(self):
        file_path = os.path.join(script_dir, "files/laura.jpeg")
        avatar = create_avatar(file_path)

        old_data = {
            "name": "test"
        }

        response = client.post(app.root_path + "/authors/create", json=old_data)
        assert response.status_code == 200

        token = response.json()['token']
        author_id = response.json()['id']

        new_data = {
            "avatar": avatar["id"]
        }

        response = client.put(
            app.root_path + f"/authors/{author_id}", 
            json=new_data,
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200

        response = client.get(app.root_path + f"/authors/{author_id}")
        assert response.status_code == 200
        assert response.json()['avatar']["id"] == new_data['avatar']

    def test_edit_author_avatar_error(self):
        file_path = os.path.join(script_dir, "files/laura.jpeg")

        old_data = {
            "name": "test"
        }

        response = client.post(app.root_path + "/authors/create", json=old_data)
        assert response.status_code == 200

        token = response.json()['token']
        author_id = response.json()['id']

        new_data = {
            "avatar": 10
        }

        response = client.put(
            app.root_path + f"/authors/{author_id}", 
            json=new_data,
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code != 200
