from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db

from ..models.author import Author
from ..models.avatar import Avatar

from .auth import generate_token

from .auth import get_author_from_token

from .avatars import AvatarResponse

router = APIRouter()

class AuthorResponse(BaseModel):
    id: int
    name: str
    avatar: Optional[AvatarResponse]

class AuthorCreateResponse(BaseModel):
    token: str
    id: int

class AuthorCreate(BaseModel):
    name: str
    avatar: Optional[int] =  None

class AuthorEdit(BaseModel):
    name: Optional[str] = None
    avatar: Optional[int] = None

@router.get("/", response_model=List[AuthorResponse])
async def get_authors(db: Session = Depends(get_db)):
    query = db.query(Author)
    return query.all()

@router.get("/{author_id}", response_model=AuthorResponse)
async def get_post(author_id: int, db: Session = Depends(get_db)):
    author = db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@router.post("/create", response_model=AuthorCreateResponse)
async def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    avatar = None
    if author.avatar is not None:
        avatar = db.query(Avatar).filter(Avatar.id == author.avatar).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
    # create author
    db_author = Author(
        name=author.name,
        avatar_id=author.avatar
    )

    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    # generate token
    token = generate_token(db_author.id)

    return AuthorCreateResponse(
        id = db_author.id,
        token = token
    )

@router.put("/{author_id}", response_model=AuthorResponse)
async def edit_author(author_id: int, new_data: AuthorEdit, db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    author = db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if author.id != token_author_id:
        raise HTTPException(status_code=401)

    # Validate avatar if provided
    updated_data = new_data.model_dump(exclude_unset=True)
    if 'avatar' in updated_data:
        avatar = db.query(Avatar).filter(Avatar.id == updated_data['avatar']).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        author.avatar_id = updated_data['avatar']
    
    # Update other fields
    if 'name' in updated_data:
        author.name = updated_data['name']
    
    # commit changes
    db.commit()
    db.refresh(author)
    return author