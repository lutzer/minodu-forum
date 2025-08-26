import os
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from .database import db_connection

from .routers import posts
from .routers import authors

api_prefix = os.getenv('API_PREFIX', "/forum")

# Initialize FastAPI app with root_path prefix
app = FastAPI(root_path=api_prefix)

app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(authors.router, prefix="/authors", tags=["authors"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    db_connection.create_tables()

@app.get("/")
async def root():
    return {"message": "Minodu Forum API"}
