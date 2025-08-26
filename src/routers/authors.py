from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db

from ..models.author import Author
from ..models.post import Post

router = APIRouter()

class AuthorResponse(BaseModel):
    id: int
    name: str
    avatar: str

class AuthorCreate(BaseModel):
    name: str
    avatar: str

@router.get("/", response_model=List[AuthorResponse])
async def get_authors(db: Session = Depends(get_db)):
    query = db.query(Author)
    return query.all()

@router.post("/", response_model=AuthorResponse)
async def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(**author.model_dump())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author