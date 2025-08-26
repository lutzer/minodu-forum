import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection

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

def create_author():
    author_data = {
        "name": "test",
        "avatar" : "test"
    }
    response = client.post(app.root_path + "/authors/", json=author_data)
    return response.json()

class TestAuthorsApi:

    def test_create_author(self):
        author_data = {
            "name": "Author1",
            "avatar" : "nothing"
        }
        response = client.post(app.root_path + "/authors/", json=author_data)        
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["name"] == author_data["name"]

    def test_fetch_authors(self):
        author_data = create_author()

        response2 = client.get(app.root_path + "/authors/")
        response2_data = response2.json()
        assert response2_data[0]["name"] == author_data["name"]