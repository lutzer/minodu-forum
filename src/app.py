import os
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from .database import db_connection

from .routers import posts

api_prefix = os.getenv('API_PREFIX', "/forum")

# Initialize FastAPI app with root_path prefix
app = FastAPI(root_path=api_prefix)

app.include_router(posts.router, prefix="/posts", tags=["posts"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    db_connection.create_tables()

@app.get("/")
async def root():
    return {"message": "Minodu Forum API"}
