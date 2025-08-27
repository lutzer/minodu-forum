from sqlalchemy import event, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

from .author import Author

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)

    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author_id = Column(Integer, ForeignKey('authors.id'), nullable=True)
    parent_id = Column(Integer, ForeignKey('posts.id'), nullable=True, default=None)

    author = relationship("Author", back_populates="posts")
    files = relationship('File', back_populates='post', uselist=True, cascade="all, delete-orphan")
    children = relationship("Post", uselist=True)