from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.author import Author
from ..models.post import Post

from ..database import get_db

from .authors import AuthorResponse

router = APIRouter()

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    author: AuthorResponse

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int

@router.get("/", response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    query = db.query(Post).join(Author)
    return query.all()

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == post.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_post = Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post