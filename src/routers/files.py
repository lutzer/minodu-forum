from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
import aiofiles
import uuid

from ..database import get_db

from ..models.file import File
from ..models.post import Post

router = APIRouter()

script_dir = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(script_dir, "../../uploads/")

class FileResponse(BaseModel):
    id: int
    filename: str
    file_path: str

class FileCreate(BaseModel):
    filename: str
    content_type: str
    file_size: str
    file_path: str
    file_hash: str

async def save_file(file: UploadFile) -> tuple:

    content = await file.read()
    
    # Generate unique filename and path
    file_extension = os.path.splitext(file.filename)[1].lower()
    if not file_extension:
        # Try to get extension from MIME type
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff"
        }
        file_extension = ext_map.get(mime_type, ".jpg")
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(UPLOAD_DIR,unique_filename)
    
    # Save file to disk
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return {
        "filename": unique_filename,
        "file_path": str(file_path),
        "file_size": 10,
        "mime_type": "test",
        "file_hash": "hash"
    }

def cleanup_file(file_path: str):
    """Remove file from disk"""
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete file {file_path}: {e}")

@router.get("/", response_model=List[FileResponse])
async def get_files(db: Session = Depends(get_db)):
    query = db.query(File)
    return query.all()

@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile, post_id: int = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    try:
        # Validate and save file
        file_info = await save_file(file)
        
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
        print(file_info)
        if 'file_info' in locals():
            cleanup_file(file_info["file_path"])
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )

    # db_file = File()
    # db.add(db_file)
    # db.commit()
    # db.refresh(db_file)
    # return db_file