from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os

from ..database import get_db

from ..config import Config

from ..models.avatar import Avatar

from .helpers import save_file, cleanup_file

router = APIRouter()

class AvatarResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    content_type: str
    file_hash: str


@router.get("/", response_model=List[AvatarResponse])
async def get_avatars(db: Session = Depends(get_db)):
    query = db.query(Avatar)
    return query.all()

@router.post("/create", response_model=AvatarResponse)
async def create_avatar(file: UploadFile, db: Session = Depends(get_db)): 
    
    try:
        # Validate and save file
        file_info = await save_file(file, Config().avatar_dir, ["image/"])
        
        # Create database record
        db_avatar = Avatar(
            filename=file_info["filename"],
            content_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            file_path=file_info["file_path"],
            file_hash=file_info["file_hash"],
        )

        db.add(db_avatar)
        db.commit()
        db.refresh(db_avatar)
        
        return db_avatar
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_info' in locals():
            cleanup_file(file_info["file_path"])
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save avatar: {str(e)}"
        )

@router.delete("/{avatar_id}")
async def delete_file(avatar_id: int, db: Session = Depends(get_db)):
    avatar = db.get(Avatar, avatar_id)

    db.delete(avatar)
    db.commit()
    
    return { "message" : "Avatar deleted" }