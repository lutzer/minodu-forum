from fastapi import UploadFile
import os
import aiofiles
import uuid
import hashlib
import mimetypes

MAX_SIZE = 1024 * 1024 * 5

async def save_file(file: UploadFile, upload_directory: str) -> tuple:
    content = await file.read()

    # check file size
    if file.size > MAX_SIZE:
        raise Exception("File size too large. Max size is: " + MAX_SIZE)

    if not (file.content_type.startswith('image/') or file.content_type.startswith('audio/')):
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

