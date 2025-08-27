import os
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

from .database import get_db_connection

from .routers import posts
from .routers import authors
from .routers import files

from .config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    get_db_connection().create_tables()
    print(Config().upload_dir)
    yield

# Initialize FastAPI app with root_path prefix
app = FastAPI(root_path=Config().api_prefix, lifespan=lifespan)

app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(authors.router, prefix="/authors", tags=["authors"])
app.include_router(files.router, prefix="/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Minodu Forum API"}
