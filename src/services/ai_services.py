from typing import Optional
import aiohttp
from ..config import Config
import logging
import os

logger = logging.getLogger(__name__)

async def transcribe_audio_async(file_path: str, language: str) -> Optional[str]:
    """Async version using aiohttp for true async HTTP requests"""
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, 
                    filename=os.path.basename(file_path),
                    content_type='audio/wav')
                form_data.add_field('language', language)

                print(Config().service_url + "/stt/transcribe")
                
                async with session.post(
                    Config().service_url + "/stt/transcribe",
                    data=form_data
                ) as response:
                    data = await response.json()
                    
        return data["text"] if data["confidence"] > 0.8 else None
    except Exception as e:
        logger.error(f"Transcribe error: {e}")
        return None