from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.posts import Post
from ..database import get_db

router = APIRouter()

class PostResponse(BaseModel):
    id: int
    author: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

class PostCreate(BaseModel):
    author: str
    title: str
    content: str

@router.get("/", response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    query = db.query(Post)
    return query.all()

@router.post("/", response_model=PostResponse)
async def get_posts(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post