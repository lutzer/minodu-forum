from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

from .avatar import Avatar

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    avatar_id = Column(Integer, ForeignKey('avatars.id'), nullable=True, default=None)

    avatar = relationship("Avatar", back_populates="authors")
    posts = relationship('Post', back_populates='author', uselist=True)
    