import pytest
import os
from fastapi.testclient import TestClient

from src.app import app
from src.database import get_db_connection

from .test_authors import create_author

script_dir = os.path.dirname(os.path.abspath(__file__))

# Create test client
client = TestClient(app)

def create_post(token: str, title: str, parent_id: int = None):
    post_data = {
        "title": title,
        "content" : "content",
        "parent_id" : parent_id
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

    def test_create_post_restricted(self):
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

    def test_reply_post(self):
        auth_token = create_author()
        post = create_post(auth_token, "parent")
        
        post_data = {
            "title": "title",
            "content" : "content",
            "parent_id" : post["id"]
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(app.root_path + "/posts/", json=post_data, headers=headers)        
        assert response.status_code == 200
       
        response = client.get(app.root_path + "/posts/")        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data[1]['parent_id'] == post["id"]

    def test_get_threads(self):
        auth_token = create_author()
        post1 = create_post(auth_token, "parent")
        post2 = create_post(auth_token, "parent")
        reply1 = create_post(auth_token, "child1", post2["id"])
        reply2 = create_post(auth_token, "child2", post2["id"])
        reply3 = create_post(auth_token, "child3", post1["id"])
       
        response = client.get(app.root_path + "/posts/threads")        
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert len(response_data[0]['children']) == 1
        assert len(response_data[1]['children']) == 2

    def test_edit_post_title(self):
        auth_token = create_author()
        post = create_post(auth_token, "old")

        post_id = post["id"]
        post_data = {
            "title": "updated"
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.put(app.root_path + f"/posts/{post_id}", json=post_data, headers=headers)        
    
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["title"] == post_data["title"]
    
    def test_edit_post_title_restricted(self):
        auth_token1 = create_author()
        auth_token2 = create_author()
        post = create_post(auth_token1, "old")

        post_id = post["id"]
        post_data = {
            "title": "updated"
        }
        headers = {"Authorization": f"Bearer {auth_token2}"}
        response = client.put(app.root_path + f"/posts/{post_id}", json=post_data, headers=headers)        
        
        assert response.status_code == 401

    def test_delete_post(self):
        auth_token = create_author()
        post = create_post(auth_token, "test")

        response = client.get(app.root_path + "/posts/")
        assert len(response.json()) == 1

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.delete(app.root_path + f"/posts/{post['id']}", headers=headers)        
        
        assert response.status_code == 200

        response = client.get(app.root_path + "/posts/")
        assert len(response.json()) == 0

    def test_delete_post_restricted(self):
        auth_token1 = create_author()
        auth_token2 = create_author()
        post = create_post(auth_token1, "test")

        headers = {"Authorization": f"Bearer {auth_token2}"}
        response = client.delete(app.root_path + f"/posts/{post['id']}", headers=headers)        
        
        assert response.status_code == 401

    def test_delete_parent_restricted(self):
        auth_token = create_author()
        post = create_post(auth_token, "parent")
        reply = create_post(auth_token, "reply", post['id'])

        response = client.delete(
            app.root_path + f"/posts/{post['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})        
        
        # dont allow deletion because it has children
        assert response.status_code == 409

        response = client.delete(
            app.root_path + f"/posts/{reply['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})        
        
        # delete reply
        assert response.status_code == 200

        response = client.delete(
            app.root_path + f"/posts/{post['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})        
        
        # now its allowed
        assert response.status_code == 200




    