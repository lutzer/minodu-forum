import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection

# Create test client
client = TestClient(app)

def create_author(name: str = "test"):
    author_data = {
        "name": name,
        "avatar" : "test"
    }
    response = client.post(app.root_path + "/authors/create", json=author_data)
    return response.json()["token"]

class TestAuthorsApi:

    def test_create_author(self):
        author_data = {
            "name": "Author1",
            "avatar" : "nothing"
        }
        response = client.post(app.root_path + "/authors/create", json=author_data)        
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data["token"]) > 0
        assert response_data["id"] >= 0

    def test_fetch_authors(self):
        author_data = {
            "name": "test",
            "avatar" : "test"
        }
        response1 = client.post(app.root_path + "/authors/create", json=author_data)

        response2 = client.get(app.root_path + "/authors/")
        response2_data = response2.json()
        assert response2_data[0]["id"] == response1.json()["id"]

    def test_edit_authors(self):
        old_data = {
            "name": "old_name",
            "avatar" : "old_avatar"
        }

        response = client.post(app.root_path + "/authors/create", json=old_data)
        token = response.json()['token']
        author_id = response.json()['id']

        new_data = {
            "name": "new_name",
            "avatar" : "new_avatar"
        }

        response = client.put(
            app.root_path + f"/authors/{author_id}", 
            json=new_data,
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()['name'] == new_data['name']
        assert response.json()['avatar'] == new_data['avatar']
