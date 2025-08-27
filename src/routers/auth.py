import jwt
import os
import time
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import Config

security = HTTPBearer()

def get_author_from_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify and decode JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, Config().jwt_secret, algorithms=[Config().jwt_algorithm])
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
    return jwt.encode(payload, Config().jwt_secret, algorithm=Config().jwt_algorithm)