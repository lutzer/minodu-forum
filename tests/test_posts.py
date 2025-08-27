import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection

from .test_authors import create_author

script_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(autouse=True)
def set_test_database_url(monkeypatch):
    # Set a test-specific database URL and create tables
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_database.db")
    get_db_connection().create_tables()
    yield
    #remove tables after tests
    get_db_connection().drop_tables()

# Create test client
client = TestClient(app)

def create_post(token: str, title: str):
    post_data = {
        "title": title,
        "content" : "content"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(app.root_path + "/posts/", json=post_data, headers=headers)   
    return response.json()

class TestPostsApi:
    def test_create_post(self):
        auth_token = create_author()

        post_data = {
            "title": "title",
            "content" : "content",
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(app.root_path + "/posts/", json=post_data, headers=headers)        
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["title"] == post_data["title"]
        assert response_data["content"] == post_data["content"]

    def test_create_post_no_auth(self):
        create_author()

        post_data = {
            "title": "title",
            "content" : "content",
        }
        headers = {"Authorization": f"Bearer dslkfhksjdhfklsdjf23oj"}
        response = client.post(app.root_path + "/posts/", json=post_data, headers=headers)        
        assert response.status_code == 401
    
    def test_fetch_post(self):
        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")

        response = client.get(app.root_path + "/posts/")        
        assert response.status_code == 200

        response_data = response.json()
        assert response_data[0]['title'] == post["title"]



    