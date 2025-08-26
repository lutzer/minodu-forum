import uvicorn
from src.app import app
from dotenv import load_dotenv
import os
import logging

load_dotenv()
port = int(os.getenv('PORT', 3001))

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

