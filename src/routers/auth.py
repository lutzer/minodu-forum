import jwt
import os
import time
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv('JWT_SECRET_KEY', "e13b50e9840a96608fa7539cc431645e")
ALGORITHM = os.getenv('JWT_ALGORITHM', "HS256")

security = HTTPBearer()

def get_author_from_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify and decode JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["author_id"]
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def generate_token(author_id: int):
    """Create a JWT access token"""
    payload = {
        "author_id": author_id,
        "created": time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)