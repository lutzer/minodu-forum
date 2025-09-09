from typing import Optional
import requests
from ..config import Config
import logging
import os

logger = logging.getLogger(__name__)

def transcribe_audio(file_path, language : str = "fr") -> Optional[str]:
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                Config().service_url + "/stt/transcribe",
                files={"file": (os.path.basename(file_path), f, "audio/wav")},
                data={"language": language}
            )
        data = response.json()
        return data["text"] if data["confidence"] > 0.8 else None
    except Exception as e:
        logger.error(f"Transciotion error: {e}")
        return None