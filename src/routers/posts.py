from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from ..models.author import Author
from ..models.post import Post
from ..models.file import File

from ..database import get_db

from .authors import AuthorResponse
from .files import FileResponse

from .auth import get_author_from_token

router = APIRouter()

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[int]

    author: AuthorResponse
    files: List[FileResponse]

class PostCreate(BaseModel):
    title: str
    content: str
    parent_id: Optional[int] = None

class ThreadResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    author: AuthorResponse
    files: List[FileResponse]
    children: List[PostResponse]

@router.get("/", response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    query = db.query(Post).join(Author).options(joinedload(Post.files))
    return query.all()

@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(db: Session = Depends(get_db)):
    query = db.query(Post).join(Author).options(joinedload(Post.files)).filter(Post.parent_id == None)
    return query.all()

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    author = db.query(Author).filter(Author.id == token_author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_post = Post(**post.model_dump(), author_id=author.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post