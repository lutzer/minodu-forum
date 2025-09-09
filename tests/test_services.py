from fastapi.testclient import TestClient
import pytest
import os
import asyncio

from src.app import app

from src.services.ai_services import transcribe_audio

from tests.test_authors import create_author
from tests.test_files import upload_file
from tests.test_posts import create_post

client = TestClient(app)

script_dir = os.path.dirname(os.path.abspath(__file__))

class TestAiServices:
    ''' These Tests require the api services to run'''

    def test_speech_to_text(self):
        file_path = os.path.join(script_dir, "files/french_sample.mp3")
        result = transcribe_audio(file_path,"fr")
        assert result != None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_audio_file_transcription(self):
        file_path = os.path.join(script_dir, "files/french_sample.mp3")

        auth_token = create_author()
        post = create_post(auth_token, "fetch_test")
        file = upload_file(post["id"],file_path, auth_token)
        file_id = file["id"]
        assert "text" in file

        while len(file["text"]) == 0:
            response = client.get(f"/files/{file_id}")
            assert response.status_code == 200
            file = response.json()
            assert "text" in file
            await asyncio.sleep(0.1)

        assert True
        
    
    
    