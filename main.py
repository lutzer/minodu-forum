import uvicorn
from src.app import app
import os
import logging

from src.config import Config


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=Config().port, reload=True)

