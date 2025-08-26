import os
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

from .database import get_db_connection

from .routers import posts
from .routers import authors

API_PREFIX = os.getenv('API_PREFIX', "/forum")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    get_db_connection().create_tables()
    yield

# Initialize FastAPI app with root_path prefix
app = FastAPI(root_path=API_PREFIX, lifespan=lifespan)

app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(authors.router, prefix="/authors", tags=["authors"])

@app.get("/")
async def root():
    return {"message": "Minodu Forum API"}
