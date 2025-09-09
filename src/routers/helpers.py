from functools import reduce
from fastapi import UploadFile
import os
import aiofiles
import uuid
import hashlib
import mimetypes

from ..config import Config

async def save_file(
        file: UploadFile, 
        upload_directory: str, 
        allowed_mime_types: list[str] = ["image/", "audio/"]) -> tuple:
    content = await file.read()

    # check file size
    if file.size > Config().max_file_size:
        raise Exception("File size too large. Max size is: " + Config().max_file_size)

    file_type_allowed = reduce(
        lambda acc, val: acc or file.content_type.startswith(val),
        allowed_mime_types,
        False)
    if not file_type_allowed:
        raise Exception("Wrong file type")

    # Generate unique filename and path
    file_extension = os.path.splitext(file.filename)[1].lower()
    if not file_extension:
        file_extension = mimetypes.guess_extension(file.content_type, strict=True) or ""

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(upload_directory, unique_filename)

    if not os.path.isdir(upload_directory):
        os.makedirs(upload_directory)
    
    # Save file to disk
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return {
        "filename": unique_filename,
        "file_path": file_path,
        "file_size": file.size,
        "mime_type": file.content_type,
        "file_hash": calculate_file_hash(file_path)
    }

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file for integrity checking"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def cleanup_file(file_path: str):
    """Remove file from disk"""
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete file {file_path}: {e}")


def get_upload_file_path(filename: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "../..", Config().upload_dir, filename)

def get_avatar_file_path(filename: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "../..", Config().avatar_dir, filename)