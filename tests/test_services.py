import pytest
import os

from src.app import app

from src.services.ai_services import transcribe_audio_async

script_dir = os.path.dirname(os.path.abspath(__file__))

class TestAiServices:
    ''' These Tests require the api services to run'''

    @pytest.mark.asyncio
    async def test_speech_to_text(self):
        file_path = os.path.join(script_dir, "files/french_sample.mp3")
        result = await transcribe_audio_async(file_path,"fr")
        assert result != None
        assert len(result) > 0
        print(result)
    
    
    