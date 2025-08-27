from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os

from ..database import get_db

from ..models.file import File
from ..models.post import Post
from ..models.author import Author

from .helpers import save_file, cleanup_file

from .auth import get_author_from_token

router = APIRouter()

script_dir = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(script_dir, "../../uploads/")

class FileResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    content_type: str
    file_hash: str

class FileCreate(BaseModel):
    filename: str
    content_type: str
    file_size: str
    file_path: str
    file_hash: str


@router.get("/", response_model=List[FileResponse])
async def get_files(db: Session = Depends(get_db)):
    query = db.query(File)
    return query.all()

@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile, post_id: int = Form(...), db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author = db.get(Author, post.author_id)
    if author.id != token_author_id:
        raise HTTPException(status_code=401)
    
    try:
        # Validate and save file
        file_info = await save_file(file, UPLOAD_DIR)
        
        # Create database record
        db_file = File(
            filename=file_info["filename"],
            content_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            file_path=file_info["file_path"],
            file_hash=file_info["file_hash"],
            post_id=post_id
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return db_file
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_info' in locals():
            cleanup_file(file_info["file_path"])
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db), token_author_id: int = Depends(get_author_from_token)):
    file = db.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.post.author.id != token_author_id:
        raise HTTPException(status_code=401)

    try:
        os.remove(file.file_path)
    finally:
        db.delete(file)
        db.commit()