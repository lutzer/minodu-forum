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
    text: str
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[int]

    author: AuthorResponse
    files: List[FileResponse]

class PostCreate(BaseModel):
    title: str
    text: str
    parent_id: Optional[int] = None

class PostEdit(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None

class ThreadResponse(BaseModel):
    id: int
    title: str
    text: str
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

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

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

@router.put("/{post_id}", response_model=PostResponse)
async def edit_post(post_id: int, new_data: PostEdit, db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author.id != token_author_id:
        raise HTTPException(status_code=401)

    # Update fields
    for key, value in new_data.model_dump().items():
        if value != None:
            setattr(post, key, value)
    
    # commit changes
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
async def delete_file(post_id: int, db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author.id != token_author_id:
        raise HTTPException(status_code=401)
    if len(post.children) > 0:
        raise HTTPException(
            status_code=409, 
            detail="Not allowed to delete post, because it has replies.")

    db.delete(post)
    db.commit()

    return { "msg" : "Post deleted." }